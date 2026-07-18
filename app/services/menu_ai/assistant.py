"""Orchestrator for the grounded "Ask AI" menu assistant.

Pipeline per question:
1. Build (cached) restaurant/menu context from the DB.
2. Retrieve the relevant menu items for the question (lexical top-K).
3. Compose a compact grounded prompt + short conversation memory.
4. Call the configured LLM (openai/gemini) with strict JSON output.
5. Validate the answer against the context (no unknown items, no
   fabricated prices). Reject and fall back if validation fails.
6. Deterministic local fallback when no provider/key or on any error,
   so the endpoint always answers and never invents dishes.
"""

import json
import logging
import os
import re
import threading
from collections import deque
from typing import Any, Deque, Dict, List, Optional, Tuple

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.menu_ai.context_builder import build_menu_context
from app.services.menu_ai.retrieval import closest_items, retrieve_relevant_items

logger = logging.getLogger(__name__)

NOT_ON_MENU_REPLY = "Sorry, that item is currently not available on our menu."
EMPTY_MENU_REPLY = (
    "Sorry, our menu is being updated right now, so I can't look up dishes yet. "
    "Please check back soon!"
)

# --- Conversation memory ------------------------------------------------------
_MEMORY_TURNS = 6  # last N (question, answer) pairs kept per session
_memory: Dict[str, Deque[Tuple[str, str]]] = {}
_memory_lock = threading.Lock()


def _memory_key(restaurant_id: int, session_id: str) -> str:
    return f"{restaurant_id}:{session_id}"


def _get_history(restaurant_id: int, session_id: str) -> List[Tuple[str, str]]:
    with _memory_lock:
        return list(_memory.get(_memory_key(restaurant_id, session_id), ()))


def _remember(restaurant_id: int, session_id: str, question: str, answer: str) -> None:
    key = _memory_key(restaurant_id, session_id)
    with _memory_lock:
        turns = _memory.setdefault(key, deque(maxlen=_MEMORY_TURNS))
        turns.append((question, answer))


# --- Prompt -------------------------------------------------------------------

def _load_prompt() -> str:
    try:
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base, "ai", "prompts", "menu_assistant_prompt.txt")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        logger.error(f"Failed to load menu assistant prompt: {e}")
        return (
            "You are a restaurant menu assistant. Answer ONLY from the provided "
            "menu context. If an item is not in the context reply exactly: "
            f"'{NOT_ON_MENU_REPLY}'. Output JSON with keys answer, "
            "matched_item_ids, out_of_menu."
        )


def _compose_user_message(
    context: Dict[str, Any],
    items_for_prompt: List[Dict[str, Any]],
    history: List[Tuple[str, str]],
    question: str,
) -> str:
    menu_lines = [
        f"- [{it['id']}] {it['name']} ({it['category']}) — ${it['price']:.2f}"
        + ("" if it["available"] else " [CURRENTLY UNAVAILABLE]")
        for it in items_for_prompt
    ]
    history_lines = [
        f"Customer: {q}\nAssistant: {a}" for q, a in history
    ] or ["(no previous messages)"]
    restaurant = context["restaurant"]
    return (
        "RESTAURANT CONTEXT\n"
        f"Name: {restaurant['name']}\n"
        f"Cuisine: {restaurant.get('cuisine_type') or 'not specified'}\n"
        f"Categories: {', '.join(context['categories']) or 'none'}\n"
        "Menu items (only these exist):\n" + "\n".join(menu_lines) + "\n\n"
        "CONVERSATION HISTORY\n" + "\n".join(history_lines) + "\n\n"
        "CUSTOMER QUESTION\n" + question
    )


# --- LLM calls ----------------------------------------------------------------

def _call_openai(system_prompt: str, user_content: str) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.3,
        "response_format": {"type": "json_object"},
    }
    with httpx.Client(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
        response = client.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)


def _call_gemini(system_prompt: str, user_content: str) -> Dict[str, Any]:
    # Key goes in a header, never the URL (URLs leak into logs on errors).
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent"
    )
    headers = {"Content-Type": "application/json", "x-goog-api-key": settings.GEMINI_API_KEY}
    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\n{user_content}"}]}],
        "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"},
    }
    with httpx.Client(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(content)


# --- Post-generation validation ----------------------------------------------

_PRICE_RE = re.compile(r"\$\s?(\d+(?:\.\d{1,2})?)")


def _validate_answer(raw: Dict[str, Any], menu_items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Rejects hallucinated answers. Returns a normalized dict or None."""
    if not isinstance(raw, dict):
        return None
    answer = raw.get("answer")
    if not isinstance(answer, str) or not answer.strip():
        return None

    ids_in_menu = {it["id"] for it in menu_items}
    matched_ids = raw.get("matched_item_ids") or []
    if not isinstance(matched_ids, list):
        matched_ids = []
    matched_ids = [i for i in matched_ids if isinstance(i, int)]
    # Any referenced id that is not a real menu item => hallucination.
    if any(i not in ids_in_menu for i in matched_ids):
        logger.warning("LLM referenced non-existent menu item ids; rejecting answer.")
        return None

    # Every price mentioned must exactly match a real menu price.
    real_prices = {f"{it['price']:.2f}" for it in menu_items}
    real_prices |= {f"{it['price']:g}" for it in menu_items}
    for match in _PRICE_RE.finditer(answer):
        p = match.group(1)
        if p not in real_prices and f"{float(p):.2f}" not in real_prices:
            logger.warning(f"LLM fabricated a price (${p}); rejecting answer.")
            return None

    return {
        "answer": answer.strip(),
        "matched_item_ids": matched_ids,
        "out_of_menu": bool(raw.get("out_of_menu", False)),
    }


# --- Local deterministic fallback --------------------------------------------

def _suggestion_sentence(items: List[Dict[str, Any]]) -> str:
    available = [it for it in items if it["available"]]
    if not available:
        return ""
    parts = [f"{it['name']} (${it['price']:.2f})" for it in available[:3]]
    return " You might enjoy " + ", ".join(parts) + " instead."


def _local_answer(
    question: str,
    context: Dict[str, Any],
    items: List[Dict[str, Any]],
    had_match: bool,
) -> Dict[str, Any]:
    """No-LLM answer built purely from DB data — safe by construction."""
    menu_items = context["menu_items"]
    if had_match:
        top = items[0]
        if not top["available"]:
            others = _suggestion_sentence([it for it in menu_items if it["id"] != top["id"]])
            answer = f"{top['name']} is currently unavailable.{others}"
        else:
            answer = (
                f"Yes! We have {top['name']} ({top['category']}) for ${top['price']:.2f}."
            )
            extras = [it for it in items[1:3] if it["available"]]
            if extras:
                answer += " We also offer " + ", ".join(
                    f"{it['name']} (${it['price']:.2f})" for it in extras
                ) + "."
        return {
            "answer": answer,
            "matched_item_ids": [it["id"] for it in items[:3]],
            "out_of_menu": False,
        }

    # Browse-style question: summarize the real menu by category.
    by_category: Dict[str, List[str]] = {}
    for it in menu_items:
        if it["available"]:
            by_category.setdefault(it["category"], []).append(
                f"{it['name']} (${it['price']:.2f})"
            )
    if not by_category:
        return {"answer": EMPTY_MENU_REPLY, "matched_item_ids": [], "out_of_menu": False}
    lines = [f"{cat}: {', '.join(names[:4])}" for cat, names in sorted(by_category.items())]
    answer = "Here's what we're serving today — " + "; ".join(lines) + "."
    return {"answer": answer, "matched_item_ids": [], "out_of_menu": False}


def _not_on_menu_answer(question: str, menu_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    suggestions = closest_items(question, [it for it in menu_items if it["available"]])
    answer = NOT_ON_MENU_REPLY + _suggestion_sentence(suggestions)
    return {
        "answer": answer,
        "matched_item_ids": [it["id"] for it in suggestions],
        "out_of_menu": True,
    }


def _dedupe(answer: str, history: List[Tuple[str, str]]) -> str:
    """Avoid replying with the identical wording twice in a row."""
    previous = {a for _, a in history}
    if answer in previous:
        return answer + " (Just as before — let me know if you'd like other suggestions!)"
    return answer


# --- Public entry point -------------------------------------------------------

def ask_menu_assistant(
    db: Session,
    restaurant_id: int,
    question: str,
    session_id: str = "default",
) -> Dict[str, Any]:
    """Answers a customer question grounded strictly in the restaurant's menu.

    Always returns {"answer", "matched_item_ids", "out_of_menu", "grounded"}.
    Raises ValueError only when the restaurant does not exist.
    """
    question = (question or "").strip()
    if not question:
        return {
            "answer": "Could you tell me a bit more about what you're looking for?",
            "matched_item_ids": [],
            "out_of_menu": False,
            "grounded": True,
        }

    context = build_menu_context(db, restaurant_id)
    if context is None:
        raise ValueError(f"Restaurant with ID {restaurant_id} not found.")

    menu_items = context["menu_items"]
    if not menu_items:
        return {
            "answer": EMPTY_MENU_REPLY,
            "matched_item_ids": [],
            "out_of_menu": False,
            "grounded": True,
        }

    items_for_prompt, had_match = retrieve_relevant_items(question, menu_items)
    history = _get_history(restaurant_id, session_id)

    # Heuristic: the question names something specific (food-like tokens) but
    # nothing on the menu matched -> deterministic "not on menu" reply.
    looks_like_item_query = not had_match and _mentions_specific_item(question)

    result: Optional[Dict[str, Any]] = None
    provider = settings.LLM_PROVIDER.lower()
    llm_available = provider in ("openai", "gemini") and (
        (provider == "openai" and settings.OPENAI_API_KEY)
        or (provider == "gemini" and settings.GEMINI_API_KEY)
    )

    if llm_available and not looks_like_item_query:
        system_prompt = _load_prompt()
        user_message = _compose_user_message(context, items_for_prompt, history, question)
        try:
            if provider == "openai":
                raw = _call_openai(system_prompt, user_message)
            else:
                raw = _call_gemini(system_prompt, user_message)
            result = _validate_answer(raw, menu_items)
        except (httpx.TimeoutException, httpx.HTTPError) as e:
            logger.error(f"Menu assistant LLM call failed ({provider}): {e}")
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            logger.error(f"Menu assistant received invalid LLM response: {e}")

    if result is None:
        if looks_like_item_query:
            result = _not_on_menu_answer(question, menu_items)
        else:
            result = _local_answer(question, context, items_for_prompt, had_match)

    result["answer"] = _dedupe(result["answer"], history)
    result["grounded"] = True
    _remember(restaurant_id, session_id, question, result["answer"])
    return result


_GENERIC_QUESTION_RE = re.compile(
    r"^(hi|hello|hey|thanks|thank you)\b|what.*(menu|have|serve|offer)|recommend|"
    r"suggest|popular|special|categor",
    re.IGNORECASE,
)


def _mentions_specific_item(question: str) -> bool:
    """True when the question looks like it names a concrete dish rather than
    browsing ('what do you have?'), greeting, or asking for recommendations."""
    return not _GENERIC_QUESTION_RE.search(question.strip())
