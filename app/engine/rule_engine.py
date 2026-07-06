"""
rule_engine.py — Member B (Simulation & Rules Engine)

Pure, deterministic business-rule checks. Every function here takes typed
inputs and returns a RuleResult — no side effects, no LLM calls, no
randomness. This is "the only component allowed to produce numbers"
(Technical Brief, Section 3.1) alongside forecasting.py and
scenario_generator.py.
"""

from __future__ import annotations

from typing import List, Optional

from app.engine.schemas import (
    DecisionInput,
    InventoryItem,
    MenuItem,
    RiskLevel,
    RuleEngineReport,
    RuleResult,
    Severity,
    StaffMember,
    Supplier,
)


# --------------------------------------------------------------------------- #
# Individual rule checks
# --------------------------------------------------------------------------- #

def check_inventory_sufficiency(
    inventory: InventoryItem,
    required_qty: float,
) -> RuleResult:
    """
    Does current stock cover the required quantity (e.g. for a bulk order
    or projected demand) without breaching the reorder level?
    """
    available_above_reorder = inventory.stock_qty - inventory.reorder_level
    sufficient = available_above_reorder >= required_qty

    if inventory.stock_qty < required_qty:
        severity = Severity.HIGH
        message = (
            f"Stock ({inventory.stock_qty:.0f}) is insufficient to cover required "
            f"quantity ({required_qty:.0f}). A supplier order is required before fulfilling this."
        )
    elif not sufficient:
        severity = Severity.MEDIUM
        message = (
            f"Stock ({inventory.stock_qty:.0f}) covers the requirement but will fall "
            f"below the reorder level ({inventory.reorder_level:.0f}) afterward."
        )
    else:
        severity = Severity.INFO
        message = "Sufficient stock available above reorder level."

    return RuleResult(
        rule_name="inventory_sufficiency",
        passed=sufficient,
        severity=severity,
        message=message,
        details={
            "stock_qty": inventory.stock_qty,
            "reorder_level": inventory.reorder_level,
            "required_qty": required_qty,
            "surplus_after_fulfillment": inventory.stock_qty - required_qty,
        },
    )


def check_supplier_delay_risk(supplier: Optional[Supplier]) -> RuleResult:
    """
    Flags risk based on supplier reliability score and average lead time.
    A supplier is considered risky if reliability is low or lead time is
    long relative to a 3-day operational buffer.
    """
    if supplier is None:
        return RuleResult(
            rule_name="supplier_delay_risk",
            passed=False,
            severity=Severity.MEDIUM,
            message="No supplier on record for this item; cannot assess delay risk.",
            details={},
        )

    lead_time_buffer_days = 3.0
    reliability_ok = supplier.reliability_score >= 0.7
    lead_time_ok = supplier.avg_lead_time_days <= lead_time_buffer_days

    passed = reliability_ok and lead_time_ok

    if not reliability_ok and not lead_time_ok:
        severity = Severity.HIGH
        message = (
            f"Supplier '{supplier.name}' has low reliability "
            f"({supplier.reliability_score:.2f}) and a long lead time "
            f"({supplier.avg_lead_time_days:.1f} days)."
        )
    elif not reliability_ok:
        severity = Severity.MEDIUM
        message = f"Supplier '{supplier.name}' has below-target reliability ({supplier.reliability_score:.2f})."
    elif not lead_time_ok:
        severity = Severity.MEDIUM
        message = (
            f"Supplier '{supplier.name}' lead time ({supplier.avg_lead_time_days:.1f} days) "
            f"exceeds the {lead_time_buffer_days:.0f}-day operational buffer."
        )
    else:
        severity = Severity.INFO
        message = f"Supplier '{supplier.name}' is reliable and within lead-time buffer."

    return RuleResult(
        rule_name="supplier_delay_risk",
        passed=passed,
        severity=severity,
        message=message,
        details={
            "reliability_score": supplier.reliability_score,
            "avg_lead_time_days": supplier.avg_lead_time_days,
            "lead_time_buffer_days": lead_time_buffer_days,
        },
    )


def check_staff_capacity(
    staff: List[StaffMember],
    additional_hours_needed: float,
    max_weekly_hours_per_staff: float = 48.0,
) -> RuleResult:
    """
    Checks whether existing staff have enough weekly headroom to absorb
    additional_hours_needed (e.g. from a bulk order or a new weekend shift)
    before breaching a configurable overtime ceiling.
    """
    total_current_hours = sum(s.weekly_hours for s in staff)
    total_capacity = len(staff) * max_weekly_hours_per_staff if staff else 0.0
    headroom = total_capacity - total_current_hours
    passed = headroom >= additional_hours_needed

    if not staff:
        severity = Severity.HIGH
        message = "No staff on record; cannot absorb any additional workload."
    elif not passed:
        severity = Severity.HIGH if additional_hours_needed - headroom > max_weekly_hours_per_staff else Severity.MEDIUM
        message = (
            f"Staff headroom ({headroom:.1f} hrs/week) is insufficient for the "
            f"additional {additional_hours_needed:.1f} hrs/week required. Hiring or "
            f"overtime approval is likely needed."
        )
    else:
        severity = Severity.INFO
        message = f"Existing staff can absorb the additional {additional_hours_needed:.1f} hrs/week."

    return RuleResult(
        rule_name="staff_capacity",
        passed=passed,
        severity=severity,
        message=message,
        details={
            "total_current_hours": total_current_hours,
            "total_capacity_hours": total_capacity,
            "headroom_hours": headroom,
            "additional_hours_needed": additional_hours_needed,
        },
    )


def check_storage_capacity(inventory: InventoryItem, incoming_qty: float) -> RuleResult:
    """
    Checks whether receiving `incoming_qty` more stock would exceed the
    item's storage_capacity.
    """
    projected_stock = inventory.stock_qty + max(0.0, incoming_qty)
    passed = projected_stock <= inventory.storage_capacity

    if passed:
        severity = Severity.INFO
        message = "Incoming stock fits within storage capacity."
    else:
        overflow = projected_stock - inventory.storage_capacity
        severity = Severity.HIGH if overflow > 0.25 * inventory.storage_capacity else Severity.MEDIUM
        message = (
            f"Incoming stock would exceed storage capacity by {overflow:.0f} units "
            f"(capacity: {inventory.storage_capacity:.0f})."
        )

    return RuleResult(
        rule_name="storage_capacity",
        passed=passed,
        severity=severity,
        message=message,
        details={
            "current_stock": inventory.stock_qty,
            "incoming_qty": incoming_qty,
            "projected_stock": projected_stock,
            "storage_capacity": inventory.storage_capacity,
        },
    )


def check_profit_feasibility(
    menu_item: MenuItem,
    projected_qty: float,
    price_change_pct: float = 0.0,
    min_acceptable_margin_pct: float = 0.15,
) -> RuleResult:
    """
    Checks whether the unit economics of the decision still clear a minimum
    acceptable margin after any price change, and reports projected gross
    profit for the given quantity.
    """
    new_sell_price = menu_item.sell_price * (1 + price_change_pct)
    unit_margin = new_sell_price - menu_item.cost_price
    margin_pct = (unit_margin / new_sell_price) if new_sell_price > 0 else -1.0
    projected_profit = unit_margin * projected_qty

    passed = margin_pct >= min_acceptable_margin_pct

    if not passed:
        severity = Severity.HIGH if margin_pct < 0 else Severity.MEDIUM
        message = (
            f"Projected margin ({margin_pct * 100:.1f}%) is below the minimum acceptable "
            f"threshold ({min_acceptable_margin_pct * 100:.0f}%)."
        )
    else:
        severity = Severity.INFO
        message = f"Projected margin ({margin_pct * 100:.1f}%) meets the minimum threshold."

    return RuleResult(
        rule_name="profit_feasibility",
        passed=passed,
        severity=severity,
        message=message,
        details={
            "new_sell_price": round(new_sell_price, 2),
            "unit_margin": round(unit_margin, 2),
            "margin_pct": round(margin_pct * 100, 2),
            "projected_qty": projected_qty,
            "projected_profit": round(projected_profit, 2),
        },
    )


def assess_operational_risk(results: List[RuleResult]) -> RiskLevel:
    """
    Rolls up individual rule results into a single overall operational risk
    level using simple, explainable thresholds (not a learned model):
        - Any HIGH-severity failure  -> HIGH
        - 2+ MEDIUM-severity failures, or exactly 1 -> MEDIUM
        - Otherwise -> LOW
    """
    failed = [r for r in results if not r.passed]
    high_failures = [r for r in failed if r.severity == Severity.HIGH]
    medium_failures = [r for r in failed if r.severity == Severity.MEDIUM]

    if high_failures:
        return RiskLevel.HIGH
    if len(medium_failures) >= 1:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


# --------------------------------------------------------------------------- #
# Orchestration class
# --------------------------------------------------------------------------- #

class RuleEngine:
    """
    Runs all rule checks against a DecisionInput and returns a single
    RuleEngineReport. This is the object the ScenarioGenerator calls once
    per scenario (optimistic/expected/pessimistic), typically with
    scenario-adjusted parameters (e.g. a worse supplier_delay_days for the
    pessimistic run).
    """

    def evaluate(
        self,
        decision: DecisionInput,
        required_qty: Optional[float] = None,
        incoming_qty: Optional[float] = None,
        supplier_override: Optional[Supplier] = None,
        supplier_delay_override_days: Optional[float] = None,
        additional_staff_hours_override: Optional[float] = None,
        price_change_pct_override: Optional[float] = None,
    ) -> RuleEngineReport:
        req_qty = decision.projected_order_qty if required_qty is None else required_qty
        req_qty = req_qty or 0.0

        supplier = supplier_override or decision.new_supplier or (
            decision.suppliers[0] if decision.suppliers else None
        )
        if supplier_delay_override_days is not None and supplier is not None:
            supplier = supplier.model_copy(update={"avg_lead_time_days": supplier_delay_override_days})

        additional_hours = (
            decision.additional_staff_hours
            if additional_staff_hours_override is None
            else additional_staff_hours_override
        )
        price_change = (
            decision.price_change_pct if price_change_pct_override is None else price_change_pct_override
        )
        incoming = req_qty if incoming_qty is None else incoming_qty

        results = [
            check_inventory_sufficiency(decision.inventory, req_qty),
            check_supplier_delay_risk(supplier),
            check_staff_capacity(decision.staff, additional_hours),
            check_storage_capacity(decision.inventory, incoming),
            check_profit_feasibility(decision.menu_item, req_qty or 1.0, price_change),
        ]

        overall_risk = assess_operational_risk(results)
        blocking = [r.rule_name for r in results if not r.passed and r.severity == Severity.HIGH]

        return RuleEngineReport(
            results=results,
            overall_risk=overall_risk,
            blocking_issues=blocking,
        )
