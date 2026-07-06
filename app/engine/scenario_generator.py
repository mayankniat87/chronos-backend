"""
scenario_generator.py — Member B (Simulation & Rules Engine)

Generates the three timelines (optimistic / expected / pessimistic) that
are the product's signature "multiple possible futures" output.

Per Technical Brief Section 2.2: timelines are parameterized scenarios fed
through the SAME deterministic formulas (RuleEngine + Forecaster) — never
three separate LLM calls. The LLM (owned by Member C) only narrates
whatever this module computes; it never alters or invents a number.
"""

from __future__ import annotations

from typing import List

from app.engine.forecasting import Forecaster
from app.engine.rule_engine import RuleEngine
from app.engine.schemas import (
    DecisionInput,
    ForecastResult,
    RiskLevel,
    RuleEngineReport,
    Scenario,
    ScenarioName,
    ScenarioParams,
    ScenarioSet,
)


# --------------------------------------------------------------------------- #
# Default scenario parameter sets
# --------------------------------------------------------------------------- #

def default_scenario_params() -> List[ScenarioParams]:
    """
    Optimistic / Expected / Pessimistic parameter sets, per Technical Brief
    Section 8.2: "demand ±15%, supplier delay 0/2/5 days".
    """
    return [
        ScenarioParams(
            name=ScenarioName.OPTIMISTIC,
            demand_multiplier=1.15,
            supplier_delay_days=0.0,
            cost_multiplier=0.97,
            label="Optimistic",
        ),
        ScenarioParams(
            name=ScenarioName.EXPECTED,
            demand_multiplier=1.0,
            supplier_delay_days=2.0,
            cost_multiplier=1.0,
            label="Expected",
        ),
        ScenarioParams(
            name=ScenarioName.PESSIMISTIC,
            demand_multiplier=0.85,
            supplier_delay_days=5.0,
            cost_multiplier=1.05,
            label="Pessimistic",
        ),
    ]


class ScenarioGenerator:
    """
    Runs the Forecaster + RuleEngine once per scenario parameter set and
    assembles the profit / revenue / inventory / staff / risk picture for
    each of the three timelines.
    """

    def __init__(self, forecaster: Forecaster | None = None, rule_engine: RuleEngine | None = None):
        self.forecaster = forecaster or Forecaster()
        self.rule_engine = rule_engine or RuleEngine()

    def _generate_one(self, decision: DecisionInput, params: ScenarioParams) -> Scenario:
        # 1. Forecast demand under this scenario's assumptions.
        extra_demand = (decision.projected_order_qty or 0.0) * params.demand_multiplier
        forecast: ForecastResult = self.forecaster.forecast_demand(
            historical_daily_sales=decision.historical_daily_sales,
            price_change_pct=decision.price_change_pct,
            supplier_delay_days=params.supplier_delay_days,
            elasticity=decision.demand_elasticity,
            extra_demand_units=extra_demand,
        )
        projected_qty = forecast.adjusted_demand

        # 2. Run rule checks with scenario-adjusted supplier delay.
        rule_report: RuleEngineReport = self.rule_engine.evaluate(
            decision,
            required_qty=projected_qty,
            incoming_qty=projected_qty,
            supplier_delay_override_days=params.supplier_delay_days,
        )

        # 3. Financials.
        adjusted_sell_price = decision.menu_item.sell_price * (1 + decision.price_change_pct)
        adjusted_cost_price = decision.menu_item.cost_price * params.cost_multiplier
        unit_margin = adjusted_sell_price - adjusted_cost_price
        profit = round(unit_margin * projected_qty, 2)

        baseline_revenue = decision.menu_item.sell_price * self.forecaster.forecast_demand(
            decision.historical_daily_sales
        ).baseline_demand
        scenario_revenue = adjusted_sell_price * projected_qty
        revenue_impact = round(scenario_revenue - baseline_revenue, 2)

        inventory_impact = round(decision.inventory.stock_qty - projected_qty, 2)

        # 4. Staff utilization: current + scenario-driven extra hours vs capacity.
        total_current_hours = sum(s.weekly_hours for s in decision.staff)
        max_capacity = len(decision.staff) * 48.0 if decision.staff else 0.0
        extra_hours = decision.additional_staff_hours * params.demand_multiplier
        projected_hours = total_current_hours + extra_hours
        staff_utilization_pct = round((projected_hours / max_capacity) * 100, 1) if max_capacity > 0 else 100.0

        # 5. Risk: escalate scenario risk one level for the pessimistic case
        #    if the rule engine didn't already flag HIGH, since compounding
        #    delay + demand miss + cost creep is itself a risk signal.
        risk_level = rule_report.overall_risk
        if params.name == ScenarioName.PESSIMISTIC and risk_level == RiskLevel.LOW:
            risk_level = RiskLevel.MEDIUM

        return Scenario(
            name=params.name,
            label=params.label,
            profit=profit,
            revenue_impact=revenue_impact,
            inventory_impact=inventory_impact,
            staff_utilization_pct=staff_utilization_pct,
            risk_level=risk_level,
            rule_report=rule_report,
            forecast=forecast,
            assumptions={
                "demand_multiplier": params.demand_multiplier,
                "supplier_delay_days": params.supplier_delay_days,
                "cost_multiplier": params.cost_multiplier,
            },
        )

    def generate_all(self, decision: DecisionInput) -> ScenarioSet:
        params_list = default_scenario_params()
        scenarios = {p.name: self._generate_one(decision, p) for p in params_list}
        return ScenarioSet(
            optimistic=scenarios[ScenarioName.OPTIMISTIC],
            expected=scenarios[ScenarioName.EXPECTED],
            pessimistic=scenarios[ScenarioName.PESSIMISTIC],
        )
