"""
Member B — Simulation & Rules Engine.

Public surface for Member A/C/D to import:

    from app.engine import (
        DecisionInput, MenuItem, InventoryItem, Supplier, StaffMember,
        RuleEngine, Forecaster, ScenarioGenerator, ConfidenceCalculator,
        SimulationEngine,
    )

SimulationEngine.run() is the single entry point Member C's
decision_service.py should call from the /decisions/simulate route.
"""

from app.engine.confidence_calculator import ConfidenceCalculator
from app.engine.forecasting import Forecaster
from app.engine.rule_engine import RuleEngine
from app.engine.scenario_generator import ScenarioGenerator
from app.engine.schemas import (
    ConfidenceResult,
    DecisionInput,
    DecisionType,
    InventoryItem,
    MenuItem,
    RiskLevel,
    RuleEngineReport,
    RuleResult,
    Scenario,
    ScenarioName,
    ScenarioSet,
    SimulationResult,
    StaffMember,
    Supplier,
)


class SimulationEngine:
    """
    Top-level facade tying together ScenarioGenerator + ConfidenceCalculator.
    This is the one call Member C's orchestration layer needs:

        engine = SimulationEngine()
        result = engine.run(decision_input)
        json_payload = result.model_dump_json()
    """

    def __init__(
        self,
        scenario_generator: ScenarioGenerator | None = None,
        confidence_calculator: ConfidenceCalculator | None = None,
    ):
        self.scenario_generator = scenario_generator or ScenarioGenerator()
        self.confidence_calculator = confidence_calculator or ConfidenceCalculator()

    def run(self, decision: DecisionInput) -> SimulationResult:
        scenarios = self.scenario_generator.generate_all(decision)
        confidence = self.confidence_calculator.calculate(decision, scenarios)

        # Recommend the expected-case scenario unless it's blocked by a
        # HIGH-severity rule failure while a less risky scenario isn't.
        recommended = ScenarioName.EXPECTED
        if scenarios.expected.rule_report.blocking_issues and not scenarios.optimistic.rule_report.blocking_issues:
            recommended = ScenarioName.OPTIMISTIC

        return SimulationResult(
            restaurant_id=decision.restaurant_id,
            decision_type=decision.decision_type,
            question_text=decision.question_text,
            scenarios=scenarios,
            confidence=confidence,
            recommended_scenario=recommended,
        )


__all__ = [
    "ConfidenceCalculator",
    "Forecaster",
    "RuleEngine",
    "ScenarioGenerator",
    "SimulationEngine",
    "ConfidenceResult",
    "DecisionInput",
    "DecisionType",
    "InventoryItem",
    "MenuItem",
    "RiskLevel",
    "RuleEngineReport",
    "RuleResult",
    "Scenario",
    "ScenarioName",
    "ScenarioSet",
    "SimulationResult",
    "StaffMember",
    "Supplier",
]
