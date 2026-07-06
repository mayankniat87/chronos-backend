"""
Unit tests for Member B's Simulation & Rules Engine.
Run with: pytest -v
"""

from __future__ import annotations

import pytest

from app.engine import SimulationEngine
from app.engine.confidence_calculator import (
    ConfidenceCalculator,
    data_completeness_score,
    historical_reliability_score,
    scenario_variance_score,
)
from app.engine.forecasting import (
    Forecaster,
    elasticity_adjusted_demand,
    moving_average,
    supplier_delay_demand_penalty,
    weighted_moving_average,
)
from app.engine.rule_engine import (
    RuleEngine,
    check_inventory_sufficiency,
    check_profit_feasibility,
    check_staff_capacity,
    check_storage_capacity,
    check_supplier_delay_risk,
)
from app.engine.sample_data import ALL_SAMPLES, sample_accept_bulk_order
from app.engine.scenario_generator import ScenarioGenerator
from app.engine.schemas import (
    InventoryItem,
    MenuItem,
    RiskLevel,
    Severity,
    StaffMember,
    Supplier,
)


# --------------------------------------------------------------------------- #
# forecasting.py
# --------------------------------------------------------------------------- #

class TestForecasting:
    def test_moving_average_basic(self):
        assert moving_average([10, 20, 30]) == 20.0

    def test_moving_average_window(self):
        assert moving_average([10, 20, 30, 100], window=2) == 65.0

    def test_moving_average_empty(self):
        assert moving_average([]) == 0.0

    def test_weighted_moving_average_recent_bias(self):
        # newest value weighted highest -> result closer to last element
        result = weighted_moving_average([10, 10, 100])
        assert result > moving_average([10, 10, 100])

    def test_weighted_moving_average_bad_weights_length(self):
        with pytest.raises(ValueError):
            weighted_moving_average([1, 2, 3], weights=[1, 2])

    def test_elasticity_price_increase_reduces_demand(self):
        demand = elasticity_adjusted_demand(100, price_change_pct=0.10, elasticity=-1.2)
        assert demand == pytest.approx(88.0)

    def test_elasticity_never_negative(self):
        demand = elasticity_adjusted_demand(10, price_change_pct=5.0, elasticity=-2.0)
        assert demand == 0.0

    def test_supplier_delay_penalty_reduces_demand(self):
        base = 100.0
        penalized = supplier_delay_demand_penalty(base, delay_days=5, sensitivity=0.03)
        assert penalized == pytest.approx(85.0)

    def test_forecaster_end_to_end(self):
        f = Forecaster()
        result = f.forecast_demand(
            historical_daily_sales=[40, 42, 45, 50],
            price_change_pct=0.1,
            supplier_delay_days=2,
        )
        assert result.baseline_demand > 0
        assert result.adjusted_demand >= 0
        assert "moving_average" in result.method or result.moving_average is not None

    def test_forecaster_no_history(self):
        f = Forecaster()
        result = f.forecast_demand(historical_daily_sales=[])
        assert result.baseline_demand == 0.0
        assert any("No historical" in n for n in result.notes)


# --------------------------------------------------------------------------- #
# rule_engine.py
# --------------------------------------------------------------------------- #

class TestRuleEngine:
    def test_inventory_sufficiency_pass(self):
        inv = InventoryItem(id="i1", menu_item_id="m1", stock_qty=100, reorder_level=20, storage_capacity=200)
        result = check_inventory_sufficiency(inv, required_qty=50)
        assert result.passed is True

    def test_inventory_sufficiency_fail_high_severity(self):
        inv = InventoryItem(id="i1", menu_item_id="m1", stock_qty=10, reorder_level=5, storage_capacity=200)
        result = check_inventory_sufficiency(inv, required_qty=50)
        assert result.passed is False
        assert result.severity == Severity.HIGH

    def test_supplier_delay_risk_no_supplier(self):
        result = check_supplier_delay_risk(None)
        assert result.passed is False

    def test_supplier_delay_risk_reliable(self):
        supplier = Supplier(id="s1", name="Good Co", reliability_score=0.9, avg_lead_time_days=1)
        result = check_supplier_delay_risk(supplier)
        assert result.passed is True

    def test_supplier_delay_risk_unreliable(self):
        supplier = Supplier(id="s2", name="Bad Co", reliability_score=0.3, avg_lead_time_days=8)
        result = check_supplier_delay_risk(supplier)
        assert result.passed is False
        assert result.severity == Severity.HIGH

    def test_staff_capacity_no_staff(self):
        result = check_staff_capacity([], additional_hours_needed=10)
        assert result.passed is False

    def test_staff_capacity_sufficient(self):
        staff = [StaffMember(id="st1", role="Cook", weekly_hours=20, hourly_cost=15)]
        result = check_staff_capacity(staff, additional_hours_needed=5)
        assert result.passed is True

    def test_storage_capacity_fail(self):
        inv = InventoryItem(id="i2", menu_item_id="m2", stock_qty=90, reorder_level=10, storage_capacity=100)
        result = check_storage_capacity(inv, incoming_qty=50)
        assert result.passed is False

    def test_profit_feasibility_healthy_margin(self):
        item = MenuItem(id="m1", name="Pizza", cost_price=3.0, sell_price=10.0)
        result = check_profit_feasibility(item, projected_qty=10)
        assert result.passed is True

    def test_profit_feasibility_thin_margin_fails(self):
        item = MenuItem(id="m1", name="Pizza", cost_price=9.5, sell_price=10.0)
        result = check_profit_feasibility(item, projected_qty=10)
        assert result.passed is False

    def test_rule_engine_full_evaluation(self):
        decision = sample_accept_bulk_order()
        engine = RuleEngine()
        report = engine.evaluate(decision)
        assert len(report.results) == 5
        assert report.overall_risk in (RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH)


# --------------------------------------------------------------------------- #
# scenario_generator.py
# --------------------------------------------------------------------------- #

class TestScenarioGenerator:
    def test_generates_three_scenarios(self):
        decision = sample_accept_bulk_order()
        gen = ScenarioGenerator()
        scenarios = gen.generate_all(decision)
        assert scenarios.optimistic.name.value == "optimistic"
        assert scenarios.expected.name.value == "expected"
        assert scenarios.pessimistic.name.value == "pessimistic"

    def test_each_scenario_has_required_fields(self):
        decision = sample_accept_bulk_order()
        gen = ScenarioGenerator()
        scenarios = gen.generate_all(decision)
        for s in scenarios.as_list():
            assert isinstance(s.profit, float)
            assert isinstance(s.revenue_impact, float)
            assert isinstance(s.inventory_impact, float)
            assert isinstance(s.staff_utilization_pct, float)
            assert s.risk_level in (RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH)

    def test_pessimistic_generally_riskier_or_equal(self):
        decision = sample_accept_bulk_order()
        gen = ScenarioGenerator()
        scenarios = gen.generate_all(decision)
        risk_order = {RiskLevel.LOW: 0, RiskLevel.MEDIUM: 1, RiskLevel.HIGH: 2}
        assert risk_order[scenarios.pessimistic.risk_level] >= risk_order[scenarios.optimistic.risk_level]

    @pytest.mark.parametrize("sample_name", list(ALL_SAMPLES.keys()))
    def test_all_samples_run_without_error(self, sample_name):
        decision = ALL_SAMPLES[sample_name]()
        gen = ScenarioGenerator()
        scenarios = gen.generate_all(decision)
        assert scenarios.optimistic is not None


# --------------------------------------------------------------------------- #
# confidence_calculator.py
# --------------------------------------------------------------------------- #

class TestConfidenceCalculator:
    def test_data_completeness_full_data(self):
        decision = sample_accept_bulk_order()
        score = data_completeness_score(decision)
        assert 0 <= score <= 100
        assert score > 50  # this sample has rich data

    def test_data_completeness_sparse_data(self):
        decision = ALL_SAMPLES["sparse_data_edge_case"]()
        score = data_completeness_score(decision)
        assert score < 60  # missing supplier/staff should hurt the score

    def test_historical_reliability_empty(self):
        assert historical_reliability_score([]) == 0.0

    def test_historical_reliability_stable_series_scores_high(self):
        stable = [50] * 30
        score = historical_reliability_score(stable)
        assert score > 90

    def test_historical_reliability_volatile_series_scores_lower(self):
        stable = [50] * 30
        volatile = [10, 90, 5, 95, 15, 85] * 5
        assert historical_reliability_score(volatile) < historical_reliability_score(stable)

    def test_scenario_variance_score_bounds(self):
        decision = sample_accept_bulk_order()
        gen = ScenarioGenerator()
        scenarios = gen.generate_all(decision)
        score = scenario_variance_score(scenarios)
        assert 0 <= score <= 100

    def test_weights_must_sum_to_one(self):
        with pytest.raises(ValueError):
            ConfidenceCalculator(weights={"data_completeness": 0.5, "historical_reliability": 0.2, "scenario_variance_stability": 0.2})

    def test_full_confidence_calculation(self):
        decision = sample_accept_bulk_order()
        gen = ScenarioGenerator()
        scenarios = gen.generate_all(decision)
        calc = ConfidenceCalculator()
        result = calc.calculate(decision, scenarios)
        assert 0 <= result.overall_score <= 100
        assert len(result.explanation_notes) == 3


# --------------------------------------------------------------------------- #
# End-to-end SimulationEngine
# --------------------------------------------------------------------------- #

class TestSimulationEngineEndToEnd:
    @pytest.mark.parametrize("sample_name", list(ALL_SAMPLES.keys()))
    def test_full_pipeline_produces_valid_json(self, sample_name):
        decision = ALL_SAMPLES[sample_name]()
        engine = SimulationEngine()
        result = engine.run(decision)

        json_str = result.model_dump_json()
        assert isinstance(json_str, str)
        assert result.confidence.overall_score >= 0
        assert result.scenarios.optimistic is not None
        assert result.scenarios.expected is not None
        assert result.scenarios.pessimistic is not None
