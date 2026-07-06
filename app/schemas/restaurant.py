from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Any
from datetime import date, datetime

# --- Common Config ---
class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Restaurant ---
class RestaurantBase(SchemaBase):
    name: str
    cuisine_type: Optional[str] = None
    cash_balance: float = 0.0

class RestaurantCreate(RestaurantBase):
    id: Optional[int] = None

class Restaurant(RestaurantBase):
    id: int


# --- Menu Item ---
class MenuItemBase(SchemaBase):
    restaurant_id: int
    name: str
    category: str
    cost_price: float
    sell_price: float

class MenuItemCreate(MenuItemBase):
    id: Optional[int] = None

class MenuItem(MenuItemBase):
    id: int


# --- Supplier ---
class SupplierBase(SchemaBase):
    restaurant_id: int
    name: str
    reliability_score: float = 1.0
    avg_lead_time_days: float = 1.0

class SupplierCreate(SupplierBase):
    id: Optional[int] = None

class Supplier(SupplierBase):
    id: int


# --- Inventory Item ---
class InventoryItemBase(SchemaBase):
    restaurant_id: int
    menu_item_id: int
    supplier_id: Optional[int] = None
    stock_qty: float = 0.0
    reorder_level: float = 0.0
    storage_capacity: float = 0.0

class InventoryItemCreate(InventoryItemBase):
    id: Optional[int] = None

class InventoryItem(InventoryItemBase):
    id: int


# --- Staff ---
class StaffBase(SchemaBase):
    restaurant_id: int
    role: str
    weekly_hours: float = 0.0
    hourly_cost: float = 0.0
    shift_pattern: Optional[str] = None

class StaffCreate(StaffBase):
    id: Optional[int] = None

class Staff(StaffBase):
    id: int


# --- Customer ---
class CustomerBase(SchemaBase):
    restaurant_id: int
    name: str
    visit_count: int = 0
    avg_spend: float = 0.0
    churn_flag: bool = False

class CustomerCreate(CustomerBase):
    id: Optional[int] = None

class Customer(CustomerBase):
    id: int


# --- Order Item ---
class OrderItemBase(SchemaBase):
    menu_item_id: int
    qty: float = 1.0
    price_at_order: float

class OrderItemCreate(OrderItemBase):
    id: Optional[int] = None

class OrderItem(OrderItemBase):
    id: int
    order_id: int


# --- Order ---
class OrderBase(SchemaBase):
    restaurant_id: int
    customer_id: Optional[int] = None
    type: str  # regular, catering, bulk
    value: float = 0.0
    date: date
    status: str = "completed"

class OrderCreate(OrderBase):
    id: Optional[int] = None
    items: Optional[List[OrderItemBase]] = []

class Order(OrderBase):
    id: int
    # Allow serialization of relationships if requested
    order_items: List[OrderItem] = []


# --- Expense ---
class ExpenseBase(SchemaBase):
    restaurant_id: int
    category: str
    amount: float
    date: date

class ExpenseCreate(ExpenseBase):
    id: Optional[int] = None

class Expense(ExpenseBase):
    id: int


# --- Decision Log (Decision Memory) ---
class DecisionLogBase(SchemaBase):
    restaurant_id: int
    decision_type: str
    inputs_json: Any
    chosen_option: str
    outcome_json: Optional[Any] = None
    decided_at: datetime = Field(default_factory=datetime.utcnow)

class DecisionLogCreate(DecisionLogBase):
    id: Optional[int] = None

class DecisionLog(DecisionLogBase):
    id: int


# --- Simulation Run ---
class SimulationRunBase(SchemaBase):
    restaurant_id: int
    question_text: str
    scenarios_json: Any
    recommendation: str
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SimulationRunCreate(SimulationRunBase):
    pass

class SimulationRun(SimulationRunBase):
    id: int


# --- Simulation Response Schema (Core Output) ---
class ScenarioResponse(SchemaBase):
    name: str  # "optimistic", "likely", "pessimistic"
    revenue: float
    cost: float
    profit: float
    risk_level: str  # "low", "medium", "high"
    metrics: dict  # specific details (inventory, staff hours, etc)

class DecisionSimulationRequest(SchemaBase):
    restaurant_id: int
    question: str
    decision_type: str
    params: dict = {}

class DecisionSimulationResponse(SchemaBase):
    restaurant_id: int
    question: str
    decision_type: str
    scenarios: List[ScenarioResponse]
    recommendation: str
    confidence: float
    causal_explanation: str
    graph_payload: Optional[dict] = None
