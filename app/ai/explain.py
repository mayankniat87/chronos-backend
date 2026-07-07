import json
import os
import logging
from typing import Any, Dict, List

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

REQUIRED_NARRATIVE_KEYS = (
    "explanation",
    "cause_chain",
    "recommendation",
    "confidence_explanation",
    "risks",
    "evidence",
    "assumptions",
)

LIST_KEYS = {"cause_chain", "risks", "evidence", "assumptions"}


def load_system_prompt() -> str:
    """Loads the system prompt from the prompts directory."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "prompts", "system_prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        logger.error(f"Failed to load system prompt: {e}")
        return "You are Chronos AI. Narration only, do not compute. Output JSON."


def _normalize_narrative(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Defensively coerces a raw LLM JSON response into the exact shape
    decision_service/SimulationResponse expect.

    This matters because the previous version returned whatever json.loads()
    produced straight through to the caller. If a live LLM call (openai/gemini)
    ever omits a key, returns null for a list field, or returns a string where
    a list was expected, that malformed dict flows all the way to FastAPI's
    response_model validation and blows up as an unhandled 500 -- which is
    exactly the failure mode a hackathon demo cannot afford once a real
    LLM_PROVIDER is switched on instead of "mock".
    """
    normalized: Dict[str, Any] = {}
    for key in REQUIRED_NARRATIVE_KEYS:
        value = raw.get(key)
        if key in LIST_KEYS:
            if isinstance(value, list):
                normalized[key] = [str(v) for v in value]
            elif value:
                normalized[key] = [str(value)]
            else:
                normalized[key] = []
        else:
            normalized[key] = str(value) if value is not None else ""
    return normalized


def generate_local_fallback(
    question: str,
    decision_type: str,
    parameters: Dict[str, Any],
    scenarios: Dict[str, Any],
    rule_violations: List[str],
    confidence: float,
) -> Dict[str, Any]:
    """
    Generates a deterministic, structured narrative matching the JSON schema.
    Used when LLM API keys are missing or remote calls fail.
    """
    timeline_a = scenarios.get("Timeline A", {})
    timeline_b = scenarios.get("Timeline B", {})
    timeline_c = scenarios.get("Timeline C", {})

    profit_a = timeline_a.get("profit", 0.0)
    profit_b = timeline_b.get("profit", 0.0)
    profit_c = timeline_c.get("profit", 0.0)

    explanation = ""
    cause_chain: List[str] = []
    recommendation = ""
    risks: List[str] = []
    evidence: List[str] = []
    assumptions: List[str] = []

    if decision_type == "accept_catering":
        val = parameters.get("order_value", 3000.0)
        days = parameters.get("days_until_event", 7)
        explanation = (
            f"Accepting the catering order valued at ${val} is expected to increase overall profit "
            f"to ${profit_b} (Expected Timeline). In the Optimistic Timeline (Timeline A), profit could reach ${profit_a} "
            f"with efficient labor and inventory management. In the Pessimistic Timeline (Timeline C), profit drops "
            f"to ${profit_c} due to possible supplier delays requiring express shipping and overtime labor costs."
        )
        cause_chain = [
            "Accept catering order -> Increase demand for stock ingredients -> Deplete inventory levels",
            "Increase inventory utilization -> Overtime staff hours required -> Increase cost of goods sold",
            f"Supplier delay (Timeline C) -> Express logistics costs -> Profit compression from ${profit_b} to ${profit_c}",
        ]
        if rule_violations:
            recommendation = (
                "Proceed with caution. Run a micro-experiment by pre-ordering 100% of required raw ingredients today "
                "to mitigate supplier lead time constraints."
            )
            risks = [f"Supply constraint: {v}" for v in rule_violations]
        else:
            recommendation = f"Approve the catering order. Lock in staff schedules at least {days} days in advance."
            risks = ["Minor staff fatigue due to increased shift volume.", "Short-term storage capacity utilization peaks."]
        evidence = [
            f"Expected timeline shows a net profit increase of ${round(profit_b - (profit_a - val), 2)} over base operations.",
            f"Confidence score of {confidence} indicates historical supplier reliability.",
        ]
        assumptions = [
            f"Event takes place in {days} days.",
            "Ingredient price volatility remains under 5%.",
            "Supplier delivery accuracy matches historical logs.",
        ]

    elif decision_type == "hire_chef":
        salary = parameters.get("monthly_salary", 3500.0)
        explanation = (
            f"Hiring another chef introduces a fixed monthly cost of ${salary}. In the Expected Timeline, "
            f"this is offset by increased order throughput, yielding a net profit of ${profit_b}. "
            f"If demand spikes (Optimistic Timeline), profit rises to ${profit_a}. However, if order volume fails to "
            f"grow (Pessimistic Timeline), the additional salary overhead results in a compressed profit of ${profit_c}."
        )
        cause_chain = [
            "Hire chef -> Increase kitchen staff capacity -> Reduce food prep times",
            "Reduce food prep times -> Higher table turnover & delivery speed -> Increase order volume",
            "Flat customer demand (Timeline C) -> Fixed salary overhead -> Compressed profit margin",
        ]
        recommendation = (
            "Hire a chef on a part-time trial basis (e.g. weekends only) to validate the demand-increase "
            "hypothesis before committing to a full-time contract."
        )
        risks = [
            "Fixed cost overhead increase without matching demand growth.",
            "Potential training period slowing down existing staff temporarily.",
        ]
        evidence = [
            f"Timeline B shows an expected profit of ${profit_b} compared to a low of ${profit_c} under Timeline C.",
            "Kitchen utilization indexes suggest weekend bottlenecks are the main throughput constraints.",
        ]
        assumptions = [
            "A new chef will immediately relieve prep times and table bottlenecks.",
            "Customer demand is constrained by prep capacity, not foot traffic.",
        ]

    elif decision_type == "change_prices":
        pct = parameters.get("price_change_pct", 0.05)
        dir_str = "increase" if pct > 0 else "decrease"
        explanation = (
            f"Implementing a {abs(pct) * 100:.1f}% price {dir_str} affects volume via customer demand elasticity. "
            f"In the Expected Timeline, profit is projected at ${profit_b}. Under Timeline A (Optimistic inelastic response), "
            f"profit reaches ${profit_a}. If customer retention drops significantly (Pessimistic Timeline), "
            f"profit declines to ${profit_c}."
        )
        cause_chain = [
            "Adjust menu prices -> Shift customer perception -> Change transaction volume",
            f"Inelastic demand (Timeline A) -> High average spend -> Maximum profit of ${profit_a}",
            "Elastic demand (Timeline C) -> High customer churn -> Drop in total transactions -> Revenue loss",
        ]
        recommendation = (
            f"Perform a pricing experiment: Apply the {abs(pct) * 100:.1f}% price {dir_str} to only 10% of the menu "
            "(e.g., beverages and sides) to observe local elasticity before making a restaurant-wide change."
        )
        risks = [
            "Customer dissatisfaction and brand erosion, leading to increased churn.",
            "Competitors undercutting prices, accelerating volume loss.",
        ]
        evidence = [
            f"Timeline C indicates a drop to ${profit_c} profit if volume elasticities hit pessimistic estimates.",
            f"The confidence score is {confidence} due to historical price-sensitivity data limitations.",
        ]
        assumptions = [
            "Baseline menu item demand follows an elasticity coefficient of -1.5.",
            "Competitors do not adjust their prices in response.",
        ]

    else:
        explanation = (
            f"Under the proposed decision, the restaurant's expected profit will be ${profit_b} (Expected Timeline). "
            f"The optimistic potential is ${profit_a}, while the pessimistic risk floor is ${profit_c}."
        )
        cause_chain = ["Implement decision -> Alter business cost/revenue structure -> Shift profit timeline"]
        recommendation = "Review the three timelines. Start with a localized experiment before rolling out fully."
        risks = ["Operational variance under pessimistic conditions.", "Increased complexity in daily operations."]
        evidence = [f"Optimistic timeline profit potential: ${profit_a}.", f"Pessimistic timeline profit floor: ${profit_c}."]
        assumptions = ["Macroeconomic factors remain stable.", "Customer foot traffic patterns follow seasonal historical averages."]

    return {
        "explanation": explanation,
        "cause_chain": cause_chain,
        "recommendation": recommendation,
        "confidence_explanation": (
            f"The confidence score is {confidence}. This is derived from a completeness check of the restaurant data, "
            f"the reliability metrics of current suppliers, and the variation of outcomes between Timeline A and C."
        ),
        "risks": risks,
        "evidence": evidence,
        "assumptions": assumptions,
    }


def explain_simulation(
    question: str,
    decision_type: str,
    parameters: Dict[str, Any],
    scenarios: Dict[str, Any],
    rule_violations: List[str],
    confidence: float,
) -> Dict[str, Any]:
    """
    Formulates prompts, calls the configured LLM API, enforces guardrails,
    and returns a structured explanation payload. Falls back to a local,
    deterministic narrative generator if no provider is configured or the
    call fails for any reason.
    """
    system_prompt = load_system_prompt()

    input_data = {
        "user_question": question,
        "decision_type": decision_type,
        "parameters": parameters,
        "rule_violations": rule_violations,
        "confidence_score": confidence,
        "scenarios": scenarios,
    }
    user_content = f"Here is the simulation context and pre-computed data:\n{json.dumps(input_data, indent=2)}"

    provider = settings.LLM_PROVIDER.lower()

    if provider == "mock" or not (settings.OPENAI_API_KEY or settings.GEMINI_API_KEY):
        if provider != "mock":
            logger.warning(f"LLM provider '{provider}' selected but no API key configured. Falling back to local narrative generator.")
        return generate_local_fallback(question, decision_type, parameters, scenarios, rule_violations, confidence)

    try:
        if provider == "openai":
            raw = _call_openai(system_prompt, user_content)
        elif provider == "gemini":
            raw = _call_gemini(system_prompt, user_content)
        else:
            logger.warning(f"Unsupported LLM provider '{provider}'. Falling back to local narrative generator.")
            return generate_local_fallback(question, decision_type, parameters, scenarios, rule_violations, confidence)

        return _normalize_narrative(raw)

    except Exception as e:
        logger.error(f"Error calling LLM API ({provider}): {e}. Falling back to local narrative generator.", exc_info=True)
        return generate_local_fallback(question, decision_type, parameters, scenarios, rule_violations, confidence)


def _call_openai(system_prompt: str, user_content: str) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": settings.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    with httpx.Client(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
        response = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        res_data = response.json()
        content = res_data["choices"][0]["message"]["content"]
        return json.loads(content)


def _call_gemini(system_prompt: str, user_content: str) -> Dict[str, Any]:
    # SECURITY: the previous version put the API key in the URL query string
    # (?key=...). httpx (and most HTTP clients/proxies/logs) include the full
    # request URL in exception messages and access logs, so any error here
    # would have leaked the Gemini key straight into application logs. Using
    # the x-goog-api-key header instead keeps the secret out of the URL.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": settings.GEMINI_API_KEY,
    }
    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\nUser Content:\n{user_content}"}]}],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
    }
    with httpx.Client(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        res_data = response.json()
        content = res_data["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(content)
