"""
forecasting.py — Member B (Simulation & Rules Engine)

Transparent, explainable statistical forecasting. Deliberately excludes
XGBoost, LightGBM, and any learned ML model, per the Chronos MVP decision to
keep every number traceable back to a formula a judge can audit on a
whiteboard (see Technical Brief, Section 2.2).

Techniques used:
    - Simple moving average
    - Weighted moving average (recent days weighted higher)
    - Simple price-elasticity adjustment

All functions are pure (no I/O, no randomness) so they are trivially unit
testable and safe to call from a request handler.
"""

from __future__ import annotations

from typing import List, Optional

from app.engine.schemas import ForecastResult


def moving_average(series: List[float], window: Optional[int] = None) -> float:
    """
    Simple moving average over the last `window` observations.
    If `window` is None or larger than the series, uses the whole series.
    Returns 0.0 for an empty series (caller should treat this as "no data").
    """
    if not series:
        return 0.0
    w = len(series) if window is None else min(window, len(series))
    recent = series[-w:]
    return sum(recent) / len(recent)


def weighted_moving_average(series: List[float], weights: Optional[List[float]] = None) -> float:
    """
    Weighted moving average. More recent observations get higher weight by
    default (linear ramp 1..n), which better reflects recent demand shifts
    than a flat moving average.

    If `weights` is provided, it must be the same length as `series`
    (aligned from oldest to newest) and will be used as-is.
    """
    if not series:
        return 0.0

    if weights is None:
        n = len(series)
        weights = [i + 1 for i in range(n)]  # oldest=1 ... newest=n

    if len(weights) != len(series):
        raise ValueError("weights must be the same length as series")

    total_weight = sum(weights)
    if total_weight == 0:
        return moving_average(series)

    weighted_sum = sum(v * w for v, w in zip(series, weights))
    return weighted_sum / total_weight


def elasticity_adjusted_demand(
    base_demand: float,
    price_change_pct: float,
    elasticity: float = -1.2,
) -> float:
    """
    Applies a simple constant-elasticity rule:
        % change in demand = elasticity * % change in price

    elasticity is negative for normal goods (price up -> demand down).
    Demand is floored at 0.

    Example: base_demand=100, price_change_pct=0.10 (+10%), elasticity=-1.2
             -> demand change = -12% -> adjusted demand = 88
    """
    demand_change_pct = elasticity * price_change_pct
    adjusted = base_demand * (1 + demand_change_pct)
    return max(0.0, adjusted)


def supplier_delay_demand_penalty(base_demand: float, delay_days: float, sensitivity: float = 0.03) -> float:
    """
    Simple rule: each day of expected supplier delay risks stockouts that
    suppress fulfilled demand by `sensitivity` (default 3%) per day, capped
    so demand can't go negative. This is intentionally a linear, explainable
    rule rather than a fitted curve.
    """
    penalty_pct = min(1.0, sensitivity * max(0.0, delay_days))
    return max(0.0, base_demand * (1 - penalty_pct))


class Forecaster:
    """
    Thin orchestration class combining the primitive forecasting functions
    into a single ForecastResult for a given decision context. Kept as a
    class (rather than a bare function) so it can hold configuration —
    e.g. a custom elasticity default — and to match the FastAPI-service
    style used elsewhere in the codebase.
    """

    def __init__(self, default_elasticity: float = -1.2, ma_window: int = 7):
        self.default_elasticity = default_elasticity
        self.ma_window = ma_window

    def forecast_demand(
        self,
        historical_daily_sales: List[float],
        price_change_pct: float = 0.0,
        supplier_delay_days: float = 0.0,
        elasticity: Optional[float] = None,
        extra_demand_units: float = 0.0,
    ) -> ForecastResult:
        """
        Produces a baseline demand estimate from history, then applies
        price-elasticity and supplier-delay adjustments in sequence.

        extra_demand_units: a known additional demand event (e.g. a bulk /
        catering order) added on top of the organic baseline forecast.
        """
        notes: List[str] = []
        elasticity = self.default_elasticity if elasticity is None else elasticity

        ma = moving_average(historical_daily_sales, self.ma_window)
        wma = weighted_moving_average(historical_daily_sales)

        if not historical_daily_sales:
            notes.append("No historical sales data supplied; baseline demand defaulted to 0.")
            baseline_demand = 0.0
        else:
            # Blend: weight the recency-aware WMA slightly more than flat MA.
            baseline_demand = 0.4 * ma + 0.6 * wma
            notes.append(
                f"Baseline blended from {self.ma_window}-day moving average ({ma:.2f}) "
                f"and weighted moving average ({wma:.2f})."
            )

        baseline_demand += max(0.0, extra_demand_units)
        if extra_demand_units:
            notes.append(f"Added {extra_demand_units:.2f} known extra demand units (e.g. bulk order).")

        demand_after_price = elasticity_adjusted_demand(baseline_demand, price_change_pct, elasticity)
        if price_change_pct:
            notes.append(
                f"Applied elasticity {elasticity:.2f} to a {price_change_pct * 100:.1f}% price change."
            )

        adjusted_demand = supplier_delay_demand_penalty(demand_after_price, supplier_delay_days)
        if supplier_delay_days:
            notes.append(f"Applied fulfillment penalty for {supplier_delay_days:.1f} day(s) of supplier delay.")

        return ForecastResult(
            method="moving_average+weighted_average+elasticity_rule",
            baseline_demand=round(baseline_demand, 2),
            adjusted_demand=round(adjusted_demand, 2),
            moving_average=round(ma, 2),
            weighted_moving_average=round(wma, 2),
            elasticity_effect_pct=round(elasticity * price_change_pct * 100, 2),
            notes=notes,
        )
