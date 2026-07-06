"""
sample_data.py — Member B (Simulation & Rules Engine)

Realistic seeded sample data for local testing / demo, covering the six
MVP decision types from Technical Brief Section 1.2:
    1. Accept a catering/bulk order
    2. Hire another chef (staff capacity is tight)
    3. Change menu prices
    4. Switch a supplier (current one is unreliable)
    5. Add weekend staff
    6. Add a combo offer

This is intentionally self-contained (no DB/network) so Member B's module
can be tested and demoed independently before Member A's Postgres layer
and Member C's orchestration service exist.
"""

from __future__ import annotations

from app.engine.schemas import (
    DecisionInput,
    DecisionType,
    InventoryItem,
    MenuItem,
    StaffMember,
    Supplier,
)

# --------------------------------------------------------------------------- #
# Shared restaurant entities ("Bella's Kitchen")
# --------------------------------------------------------------------------- #

MARGHERITA_PIZZA = MenuItem(
    id="menu_001", name="Margherita Pizza", cost_price=3.50, sell_price=9.00
)

RELIABLE_SUPPLIER = Supplier(
    id="sup_001", name="FreshFarm Distributors", reliability_score=0.92, avg_lead_time_days=1.5
)

UNRELIABLE_SUPPLIER = Supplier(
    id="sup_002", name="BudgetBulk Co.", reliability_score=0.55, avg_lead_time_days=6.0
)

TIGHT_INVENTORY = InventoryItem(
    id="inv_001", menu_item_id="menu_001", stock_qty=120, reorder_level=40, storage_capacity=300
)

FULL_STAFF_ROSTER = [
    StaffMember(id="staff_001", role="Head Chef", weekly_hours=45, hourly_cost=22.0),
    StaffMember(id="staff_002", role="Line Cook", weekly_hours=40, hourly_cost=16.0),
    StaffMember(id="staff_003", role="Server", weekly_hours=30, hourly_cost=12.0),
]

# 21 days of daily units sold for Margherita Pizza — mild upward trend, realistic noise.
HISTORICAL_DAILY_SALES = [
    38, 41, 35, 44, 50, 61, 58,
    40, 43, 39, 47, 53, 65, 60,
    42, 45, 41, 49, 55, 68, 63,
]


# --------------------------------------------------------------------------- #
# Scenario 1: Accept a large catering/bulk order
# --------------------------------------------------------------------------- #

def sample_accept_bulk_order() -> DecisionInput:
    return DecisionInput(
        restaurant_id="rest_001",
        decision_type=DecisionType.ACCEPT_BULK_ORDER,
        question_text="Should we accept a 150-pizza catering order for Saturday?",
        menu_item=MARGHERITA_PIZZA,
        inventory=TIGHT_INVENTORY,
        suppliers=[RELIABLE_SUPPLIER],
        staff=FULL_STAFF_ROSTER,
        historical_daily_sales=HISTORICAL_DAILY_SALES,
        projected_order_qty=150,
        price_change_pct=0.0,
        additional_staff_hours=8.0,
        cash_balance=12000.0,
    )


# --------------------------------------------------------------------------- #
# Scenario 2: Hire another chef (staff already near capacity)
# --------------------------------------------------------------------------- #

def sample_hire_staff() -> DecisionInput:
    tight_staff = [
        StaffMember(id="staff_001", role="Head Chef", weekly_hours=47, hourly_cost=22.0),
        StaffMember(id="staff_002", role="Line Cook", weekly_hours=46, hourly_cost=16.0),
    ]
    return DecisionInput(
        restaurant_id="rest_001",
        decision_type=DecisionType.HIRE_STAFF,
        question_text="Should we hire a second line cook for the weekend rush?",
        menu_item=MARGHERITA_PIZZA,
        inventory=TIGHT_INVENTORY,
        suppliers=[RELIABLE_SUPPLIER],
        staff=tight_staff,
        historical_daily_sales=HISTORICAL_DAILY_SALES,
        projected_order_qty=0,
        additional_staff_hours=35.0,  # a new full-time hire's hours
        cash_balance=8000.0,
    )


# --------------------------------------------------------------------------- #
# Scenario 3: Change menu price (+12%)
# --------------------------------------------------------------------------- #

def sample_change_price() -> DecisionInput:
    return DecisionInput(
        restaurant_id="rest_001",
        decision_type=DecisionType.CHANGE_PRICE,
        question_text="What happens if we raise the Margherita Pizza price by 12%?",
        menu_item=MARGHERITA_PIZZA,
        inventory=TIGHT_INVENTORY,
        suppliers=[RELIABLE_SUPPLIER],
        staff=FULL_STAFF_ROSTER,
        historical_daily_sales=HISTORICAL_DAILY_SALES,
        projected_order_qty=0,
        price_change_pct=0.12,
        demand_elasticity=-1.2,
        cash_balance=10000.0,
    )


# --------------------------------------------------------------------------- #
# Scenario 4: Switch supplier (current one is unreliable)
# --------------------------------------------------------------------------- #

def sample_switch_supplier() -> DecisionInput:
    return DecisionInput(
        restaurant_id="rest_001",
        decision_type=DecisionType.SWITCH_SUPPLIER,
        question_text="Should we switch from BudgetBulk Co. to FreshFarm Distributors?",
        menu_item=MARGHERITA_PIZZA,
        inventory=TIGHT_INVENTORY,
        suppliers=[UNRELIABLE_SUPPLIER],
        staff=FULL_STAFF_ROSTER,
        historical_daily_sales=HISTORICAL_DAILY_SALES,
        projected_order_qty=60,
        new_supplier=RELIABLE_SUPPLIER,
        cash_balance=10000.0,
    )


# --------------------------------------------------------------------------- #
# Scenario 5: Add weekend staff
# --------------------------------------------------------------------------- #

def sample_add_weekend_staff() -> DecisionInput:
    return DecisionInput(
        restaurant_id="rest_001",
        decision_type=DecisionType.ADD_WEEKEND_STAFF,
        question_text="Should we add a weekend-only server for Sat/Sun shifts?",
        menu_item=MARGHERITA_PIZZA,
        inventory=TIGHT_INVENTORY,
        suppliers=[RELIABLE_SUPPLIER],
        staff=FULL_STAFF_ROSTER,
        historical_daily_sales=HISTORICAL_DAILY_SALES,
        projected_order_qty=0,
        additional_staff_hours=16.0,
        cash_balance=9500.0,
    )


# --------------------------------------------------------------------------- #
# Scenario 6: Add a combo offer (bundle price, i.e. effective price decrease)
# --------------------------------------------------------------------------- #

def sample_add_combo_offer() -> DecisionInput:
    return DecisionInput(
        restaurant_id="rest_001",
        decision_type=DecisionType.ADD_COMBO_OFFER,
        question_text="What if we bundle a pizza + drink combo at an effective 8% discount?",
        menu_item=MARGHERITA_PIZZA,
        inventory=TIGHT_INVENTORY,
        suppliers=[RELIABLE_SUPPLIER],
        staff=FULL_STAFF_ROSTER,
        historical_daily_sales=HISTORICAL_DAILY_SALES,
        projected_order_qty=0,
        price_change_pct=-0.08,
        demand_elasticity=-1.5,  # combos tend to be more elastic
        cash_balance=10000.0,
    )


# --------------------------------------------------------------------------- #
# Edge case: sparse/incomplete data, to exercise the confidence calculator's
# low-completeness path.
# --------------------------------------------------------------------------- #

def sample_sparse_data_decision() -> DecisionInput:
    return DecisionInput(
        restaurant_id="rest_002",
        decision_type=DecisionType.GENERIC,
        question_text="New location with almost no history yet — should we accept a 40-unit order?",
        menu_item=MenuItem(id="menu_010", name="Veggie Wrap", cost_price=2.00, sell_price=6.50),
        inventory=InventoryItem(
            id="inv_010", menu_item_id="menu_010", stock_qty=25, reorder_level=10, storage_capacity=80
        ),
        suppliers=[],
        staff=[],
        historical_daily_sales=[12, 15],  # only 2 days of data
        projected_order_qty=40,
        cash_balance=1500.0,
    )


ALL_SAMPLES = {
    "accept_bulk_order": sample_accept_bulk_order,
    "hire_staff": sample_hire_staff,
    "change_price": sample_change_price,
    "switch_supplier": sample_switch_supplier,
    "add_weekend_staff": sample_add_weekend_staff,
    "add_combo_offer": sample_add_combo_offer,
    "sparse_data_edge_case": sample_sparse_data_decision,
}
