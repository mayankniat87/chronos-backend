"""Lexical retrieval of relevant menu items for a customer question.

No embedding service is configured in this project, so retrieval is a
deterministic token-overlap + fuzzy scorer. It selects the top-K relevant
menu items so the prompt stays small; if nothing scores above the floor,
the whole (compact) menu is sent instead, so the model can still answer
browse-style questions like "what do you have?".
"""

import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Tuple

_STOPWORDS = {
    "a", "an", "the", "do", "does", "you", "your", "have", "has", "is", "are",
    "any", "what", "whats", "which", "can", "i", "get", "me", "on", "in", "of",
    "for", "to", "with", "menu", "there", "how", "much", "price", "cost",
    "serve", "sell", "and", "or", "please", "want", "would", "like", "some",
}

MAX_ITEMS = 12
# High enough that unrelated words ("platter" vs "spaghetti" ~0.5) don't
# count as matches, low enough to still catch typos ("margarita" ~0.84).
SCORE_FLOOR = 0.72


def _tokens(text: str) -> List[str]:
    # len >= 3 guards against fragments like the "s" in "what's", which would
    # otherwise substring-match almost every menu item name.
    return [
        t
        for t in re.findall(r"[a-z0-9]+", text.lower())
        if t not in _STOPWORDS and len(t) >= 3
    ]


def _fuzzy(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def score_item(question_tokens: List[str], item: Dict[str, Any]) -> float:
    """Best fuzzy/exact match between question tokens and item name/category."""
    item_tokens = _tokens(f"{item['name']} {item['category']}")
    if not question_tokens or not item_tokens:
        return 0.0
    best = 0.0
    for qt in question_tokens:
        for it in item_tokens:
            if qt == it:
                best = max(best, 1.0)
            elif qt in it or it in qt:
                best = max(best, 0.85)
            else:
                best = max(best, _fuzzy(qt, it))
    return best


def retrieve_relevant_items(
    question: str, menu_items: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], bool]:
    """Returns (items_for_prompt, had_strong_match).

    - Strong matches -> top-K scored items only (small prompt).
    - No strong match (generic/browse question) -> full menu, and
      had_strong_match=False so the caller knows the question named
      nothing recognizable.
    """
    qtokens = _tokens(question)
    scored = sorted(
        ((score_item(qtokens, item), item) for item in menu_items),
        key=lambda pair: pair[0],
        reverse=True,
    )
    strong = [item for s, item in scored if s >= SCORE_FLOOR][:MAX_ITEMS]
    if strong:
        return strong, True
    return list(menu_items), False


def closest_items(
    question: str, menu_items: List[Dict[str, Any]], limit: int = 3
) -> List[Dict[str, Any]]:
    """Best-effort 'closest dishes' for the not-on-menu fallback."""
    qtokens = _tokens(question)
    scored = sorted(
        ((score_item(qtokens, item), item) for item in menu_items),
        key=lambda pair: pair[0],
        reverse=True,
    )
    return [item for s, item in scored[:limit] if s > 0.2]
