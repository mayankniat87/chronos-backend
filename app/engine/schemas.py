"""
Shared data contracts for the Chronos Simulation & Rules Engine (Member B).

These are Pydantic models so they can be imported directly into FastAPI
route handlers (Member A / Member C) as request/response schemas without
any adaptation layer.

Design notes:
- All engine functions are pure and deterministic. Nothing in this module
  or the rest of the engine package makes a network or LLM call.
- Every output model is JSON-serializable via `.model_dump()` / `.model_dump_json()`.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# --------------------------------------------------------------------------- #
# Enums
# --------------------------------------------------------------------------- #

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionType(str, Enum):
    ACCEPT_BULK_ORDER = "accept_bulk_order"
    HIRE_STAFF = "hire_staff"
    CHANGE_PRICE = "change_price"
    SWITCH_SUPPLIER = "switch_supplier"
    ADD_WEEKEND_STAFF = "add_weekend_staff"
    ADD_COMBO_OFFER = "add_combo_offer"
    GENERIC = "generic"


class ScenarioName(str, Enum):
    OPTIMISTIC = "optimistic"
    EXPECTED = "expected"
    PESSIMISTIC = "pessimistic"


# --------------------------------------------------------------------------- #
# Input entities (mirror the Postgres tables in Section 7 of the brief)
# --------------------------------------------------------------------------- #

class MenuItem(BaseModel):
    id: str
    name: str
    cost_price: float = Field(..., ge=0)
    sell_price: float = Field(..., ge=0)

    @property
    def unit_margin(self) -> float:
        return self.sell_price - self.cost_price


class InventoryItem(BaseModel):
    id: str
    menu_item_id: str
    stock_qty: float = Field(..., ge=0)
    reorder_level: float = Field(..., ge=0)
    storage_capacity: float = Field(..., ge=0)


class Supplier(BaseModel):
    id: str
    name: str
    reliability_score: float = Field(..., ge=0, le=1, description="0=unreliable, 1=fully reliable")
    avg_lead_time_days: float = Field(..., ge=0)

    @field_validator("reliability_score")
    @classmethod
    def _clamp_reliability(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class StaffMember(BaseModel):
    id: str
    role: str
    weekly_hours: float = Field(..., ge=0)
    hourly_cost: float = Field(..., ge=0)


# --------------------------------------------------------------------------- #
# Decision input — what the API layer hands to the engine
# --------------------------------------------------------------------------- #

class DecisionInput(BaseModel):
    """
    The single object the engine needs to evaluate a decision.
    Member C's orchestration service (decision_service.py) is expected to
    assemble this from Postgres before calling the engine.
    """

    restaurant_id: str
    decision_type: DecisionType = DecisionType.GENERIC
    question_text: Optional[str] = None

    menu_item: MenuItem
    inventory: InventoryItem
    suppliers: List[Supplier] = Field(default_factory=list)
    staff: List[StaffMember] = Field(default_factory=list)

    historical_daily_sales: List[float] = Field(
        default_factory=list,
        description="Recent daily units sold for this menu item, oldest first.",
    )
    historical_data_days_expected: int = Field(
        default=30,
        description="How many days of history we'd ideally like, used for data completeness scoring.",
    )

    # Decision-specific levers (all optional — only the relevant ones need be set)
    projected_order_qty: Optional[float] = Field(
        default=None, description="Extra units required, e.g. for a bulk/catering order."
    )
    price_change_pct: float = Field(default=0.0, description="e.g. 0.10 for +10%")
    additional_staff_hours: float = Field(default=0.0)
    new_supplier: Optional[Supplier] = None
    cash_balance: float = Field(default=0.0, ge=0)

    demand_elasticity: float = Field(
        default=-1.2,
        description="Price elasticity of demand. Negative: price up -> demand down.",
    )


# --------------------------------------------------------------------------- #
# Rule Engine outputs
# --------------------------------------------------------------------------- #

class RuleResult(BaseModel):
    rule_name: str
    passed: bool
    severity: Severity
    message: str
    details: Dict[str, float] = Field(default_factory=dict)


class RuleEngineReport(BaseModel):
    results: List[RuleResult]
    overall_risk: RiskLevel
    blocking_issues: List[str] = Field(
        default_factory=list, description="rule_names of failed HIGH severity rules"
    )

    @property
    def all_passed(self) -> bool:
        return all(r.passed for r in self.results)


# --------------------------------------------------------------------------- #
# Forecasting outputs
# --------------------------------------------------------------------------- #

class ForecastResult(BaseModel):
    method: str
    baseline_demand: float
    adjusted_demand: float
    moving_average: Optional[float] = None
    weighted_moving_average: Optional[float] = None
    elasticity_effect_pct: float = 0.0
    notes: List[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Scenario Generator outputs
# --------------------------------------------------------------------------- #

class ScenarioParams(BaseModel):
    name: ScenarioName
    demand_multiplier: float
    supplier_delay_days: float
    cost_multiplier: float = 1.0
    label: str


class Scenario(BaseModel):
    name: ScenarioName
    label: str
    profit: float
    revenue_impact: float
    inventory_impact: float
    staff_utilization_pct: float
    risk_level: RiskLevel
    rule_report: RuleEngineReport
    forecast: ForecastResult
    assumptions: Dict[str, float] = Field(default_factory=dict)


class ScenarioSet(BaseModel):
    optimistic: Scenario
    expected: Scenario
    pessimistic: Scenario

    def as_list(self) -> List[Scenario]:
        return [self.optimistic, self.expected, self.pessimistic]


# --------------------------------------------------------------------------- #
# Confidence Calculator outputs
# --------------------------------------------------------------------------- #

class ConfidenceBreakdown(BaseModel):
    data_completeness: float = Field(..., ge=0, le=100)
    historical_reliability: float = Field(..., ge=0, le=100)
    scenario_variance_stability: float = Field(..., ge=0, le=100)


class ConfidenceResult(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    breakdown: ConfidenceBreakdown
    weights: Dict[str, float]
    explanation_notes: List[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Top-level simulation output — this is the JSON the API layer persists to
# simulation_runs and returns to the frontend / hands to the LLM explanation
# layer (LLM only narrates this, never edits the numbers).
# --------------------------------------------------------------------------- #

class SimulationResult(BaseModel):
    restaurant_id: str
    decision_type: DecisionType
    question_text: Optional[str] = None
    scenarios: ScenarioSet
    confidence: ConfidenceResult
    recommended_scenario: ScenarioName
    generated_by: str = "chronos-rule-engine-v1"
