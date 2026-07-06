"""
confidence_calculator.py — Member B (Simulation & Rules Engine)

Deterministic 0-100 confidence score for a simulation run, computed from:
    1. Data completeness    — how much of the expected input data we actually have
    2. Historical reliability — how much/how stable the historical sales data is
    3. Scenario variance stability — how much the three scenarios agree with
       each other (low agreement = lower confidence)

Per Technical Brief Section 8.2 Step 4: "a deterministic score ... never
guessed by the LLM." No randomness, no learned weights — just transparent,
auditable arithmetic so it can be explained to judges on demand.
"""

from __future__ import annotations

from statistics import pstdev
from typing import List

from app.engine.schemas import (
    ConfidenceBreakdown,
    ConfidenceResult,
    DecisionInput,
    Scenario,
    ScenarioSet,
)

# Weights are explicit and sum to 1.0 — tweak here only, never inline elsewhere.
DEFAULT_WEIGHTS = {
    "data_completeness": 0.35,
    "historical_reliability": 0.30,
    "scenario_variance_stability": 0.35,
}


def data_completeness_score(decision: DecisionInput) -> float:
    """
    Rewards having: enough historical sales days, a known supplier, and a
    non-empty staff roster. Each contributes independently so partial data
    still yields a partial (not zero) score.
    """
    score = 0.0
    notes_weight_total = 0.0

    # Historical sales coverage (up to 50 points)
    expected_days = max(1, decision.historical_data_days_expected)
    have_days = len(decision.historical_daily_sales)
    coverage_ratio = min(1.0, have_days / expected_days)
    score += coverage_ratio * 50
    notes_weight_total += 50

    # Supplier on record (20 points)
    has_supplier = bool(decision.suppliers or decision.new_supplier)
    score += 20 if has_supplier else 0
    notes_weight_total += 20

    # Staff roster present (15 points)
    has_staff = bool(decision.staff)
    score += 15 if has_staff else 0
    notes_weight_total += 15

    # Inventory numbers sane / non-placeholder (15 points)
    inv = decision.inventory
    inventory_ok = inv.storage_capacity > 0 and inv.reorder_level >= 0
    score += 15 if inventory_ok else 0
    notes_weight_total += 15

    return round((score / notes_weight_total) * 100, 2)


def historical_reliability_score(historical_daily_sales: List[float]) -> float:
    """
    Rewards having (a) enough data points and (b) low relative volatility in
    that data (a wildly swinging series is less trustworthy to forecast
    from, even if it's long).
    """
    n = len(historical_daily_sales)
    if n == 0:
        return 0.0

    # Length component: saturates at 30 days of history.
    length_score = min(1.0, n / 30) * 60

    mean = sum(historical_daily_sales) / n
    if mean <= 0 or n < 2:
        stability_score = 30.0  # not enough info to judge volatility either way
    else:
        std_dev = pstdev(historical_daily_sales)
        coefficient_of_variation = std_dev / mean
        # CoV of 0 -> full 40 points; CoV >= 1.0 (100% swings) -> 0 points.
        stability_score = max(0.0, 1 - min(1.0, coefficient_of_variation)) * 40

    return round(length_score + stability_score, 2)


def scenario_variance_score(scenarios: ScenarioSet) -> float:
    """
    Measures how much the three scenarios' profit outcomes agree. Small
    spread between optimistic/expected/pessimistic -> high confidence the
    range is well understood. Wide spread relative to the expected case's
    magnitude -> lower confidence.
    """
    profits = [s.profit for s in scenarios.as_list()]
    expected_profit = scenarios.expected.profit

    spread = max(profits) - min(profits)
    denominator = max(abs(expected_profit), 1.0)  # avoid divide-by-zero, floor at 1
    relative_spread = spread / denominator

    # relative_spread of 0 -> 100; relative_spread >= 2.0 (200% of expected profit) -> 0
    score = max(0.0, 1 - min(1.0, relative_spread / 2.0)) * 100
    return round(score, 2)


class ConfidenceCalculator:
    """Combines the three component scores into one overall confidence score."""

    def __init__(self, weights: dict | None = None):
        self.weights = weights or DEFAULT_WEIGHTS
        total = sum(self.weights.values())
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Confidence weights must sum to 1.0, got {total}")

    def calculate(self, decision: DecisionInput, scenarios: ScenarioSet) -> ConfidenceResult:
        completeness = data_completeness_score(decision)
        reliability = historical_reliability_score(decision.historical_daily_sales)
        variance_stability = scenario_variance_score(scenarios)

        overall = (
            completeness * self.weights["data_completeness"]
            + reliability * self.weights["historical_reliability"]
            + variance_stability * self.weights["scenario_variance_stability"]
        )

        notes = [
            f"Data completeness {completeness:.1f}/100 "
            f"(historical days, supplier, staff, and inventory data present).",
            f"Historical reliability {reliability:.1f}/100 "
            f"(based on {len(decision.historical_daily_sales)} days of sales history and its volatility).",
            f"Scenario variance stability {variance_stability:.1f}/100 "
            f"(agreement between optimistic/expected/pessimistic profit outcomes).",
        ]

        return ConfidenceResult(
            overall_score=round(overall, 2),
            breakdown=ConfidenceBreakdown(
                data_completeness=completeness,
                historical_reliability=reliability,
                scenario_variance_stability=variance_stability,
            ),
            weights=self.weights,
            explanation_notes=notes,
        )
