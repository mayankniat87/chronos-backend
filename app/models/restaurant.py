from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.core.database import Base

def _utcnow():
    return datetime.now(timezone.utc)

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    cuisine_type = Column(String, nullable=True)
    cash_balance = Column(Float, nullable=False, default=0.0)

    # Relationships
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    suppliers = relationship("Supplier", back_populates="restaurant", cascade="all, delete-orphan")
    inventory_items = relationship("InventoryItem", back_populates="restaurant", cascade="all, delete-orphan")
    staff = relationship("Staff", back_populates="restaurant", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="restaurant", cascade="all, delete-orphan")
    decisions_log = relationship("DecisionLog", back_populates="restaurant", cascade="all, delete-orphan")
    simulation_runs = relationship("SimulationRun", back_populates="restaurant", cascade="all, delete-orphan")


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    cost_price = Column(Float, nullable=False)
    sell_price = Column(Float, nullable=False)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="menu_items")
    inventory_items = relationship("InventoryItem", back_populates="menu_item", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="menu_item", cascade="all, delete-orphan")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    reliability_score = Column(Float, nullable=False, default=1.0)
    avg_lead_time_days = Column(Float, nullable=False, default=1.0)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="suppliers")
    inventory_items = relationship("InventoryItem", back_populates="supplier")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True, index=True)
    stock_qty = Column(Float, nullable=False, default=0.0)
    reorder_level = Column(Float, nullable=False, default=0.0)
    storage_capacity = Column(Float, nullable=False, default=0.0)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="inventory_items")
    menu_item = relationship("MenuItem", back_populates="inventory_items")
    supplier = relationship("Supplier", back_populates="inventory_items")


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String, nullable=False)
    weekly_hours = Column(Float, nullable=False, default=0.0)
    hourly_cost = Column(Float, nullable=False, default=0.0)
    shift_pattern = Column(String, nullable=True)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="staff")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    visit_count = Column(Integer, nullable=False, default=0)
    avg_spend = Column(Float, nullable=False, default=0.0)
    churn_flag = Column(Boolean, nullable=False, default=False)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="customers")
    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    type = Column(String, nullable=False)  # e.g., 'regular', 'catering', 'bulk'
    value = Column(Float, nullable=False, default=0.0)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="completed")

    # Relationships
    restaurant = relationship("Restaurant", back_populates="orders")
    customer = relationship("Customer", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id", ondelete="CASCADE"), nullable=False, index=True)
    qty = Column(Float, nullable=False, default=1.0)
    price_at_order = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="order_items")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="expenses")


class DecisionLog(Base):
    __tablename__ = "decisions_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    decision_type = Column(String, nullable=False)  # hire, pricing, supplier, combo, etc.
    inputs_json = Column(JSON, nullable=False)
    chosen_option = Column(String, nullable=False)
    outcome_json = Column(JSON, nullable=True)
    decided_at = Column(DateTime, nullable=False, default=_utcnow)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="decisions_log")


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(String, nullable=False)
    scenarios_json = Column(JSON, nullable=False)
    recommendation = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=_utcnow)

    # Relationships
    restaurant = relationship("Restaurant", back_populates="simulation_runs")
