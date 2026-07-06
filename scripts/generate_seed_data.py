import pandas as pd
import json
import os

os.makedirs("seed_data", exist_ok=True)

# 1. Restaurants
pd.DataFrame([
    {"id": 1, "name": "Chronos Demo Diner", "cuisine_type": "American", "cash_balance": 25000.0}
]).to_csv("seed_data/restaurants.csv", index=False)

# 2. Suppliers
pd.DataFrame([
    {"id": 1, "restaurant_id": 1, "name": "Fresh Farms Produce", "reliability_score": 0.9, "avg_lead_time_days": 2},
    {"id": 2, "restaurant_id": 1, "name": "Premium Meats Inc.", "reliability_score": 0.95, "avg_lead_time_days": 1},
    {"id": 3, "restaurant_id": 1, "name": "Global Beverages", "reliability_score": 0.8, "avg_lead_time_days": 3}
]).to_csv("seed_data/suppliers.csv", index=False)

# 3. Menu Items
pd.DataFrame([
    {"id": 1, "restaurant_id": 1, "name": "Classic Burger", "category": "Mains", "cost_price": 3.5, "sell_price": 12.0},
    {"id": 2, "restaurant_id": 1, "name": "Fries", "category": "Sides", "cost_price": 0.5, "sell_price": 4.0},
    {"id": 3, "restaurant_id": 1, "name": "Coke", "category": "Drinks", "cost_price": 0.3, "sell_price": 2.5}
]).to_csv("seed_data/menu_items.csv", index=False)

# 4. Inventory
pd.DataFrame([
    {"id": 1, "restaurant_id": 1, "menu_item_id": 1, "supplier_id": 2, "stock_qty": 150, "reorder_level": 50, "storage_capacity": 500},
    {"id": 2, "restaurant_id": 1, "menu_item_id": 2, "supplier_id": 1, "stock_qty": 300, "reorder_level": 100, "storage_capacity": 1000},
    {"id": 3, "restaurant_id": 1, "menu_item_id": 3, "supplier_id": 3, "stock_qty": 500, "reorder_level": 200, "storage_capacity": 2000}
]).to_csv("seed_data/inventory_items.csv", index=False)

# 5. Staff
pd.DataFrame([
    {"id": 1, "restaurant_id": 1, "role": "Head Chef", "weekly_hours": 50, "hourly_cost": 30.0, "shift_pattern": "Morning"},
    {"id": 2, "restaurant_id": 1, "role": "Line Cook", "weekly_hours": 40, "hourly_cost": 20.0, "shift_pattern": "Evening"},
    {"id": 3, "restaurant_id": 1, "role": "Server", "weekly_hours": 30, "hourly_cost": 15.0, "shift_pattern": "Split"}
]).to_csv("seed_data/staff.csv", index=False)

# 6. Customers
pd.DataFrame([
    {"id": 1, "restaurant_id": 1, "name": "Alice", "visit_count": 5, "avg_spend": 25.0, "churn_flag": False},
    {"id": 2, "restaurant_id": 1, "name": "Bob", "visit_count": 2, "avg_spend": 15.0, "churn_flag": True}
]).to_csv("seed_data/customers.csv", index=False)

# 7. Orders
pd.DataFrame([
    {"id": 1, "restaurant_id": 1, "customer_id": 1, "type": "regular", "value": 28.5, "date": "2023-10-01", "status": "completed"},
    {"id": 2, "restaurant_id": 1, "customer_id": 2, "type": "regular", "value": 15.0, "date": "2023-10-02", "status": "completed"}
]).to_csv("seed_data/orders.csv", index=False)

# 8. Order Items
pd.DataFrame([
    {"id": 1, "order_id": 1, "menu_item_id": 1, "qty": 2, "price_at_order": 12.0},
    {"id": 2, "order_id": 1, "menu_item_id": 2, "qty": 1, "price_at_order": 4.5},
    {"id": 3, "order_id": 2, "menu_item_id": 1, "qty": 1, "price_at_order": 12.0}
]).to_csv("seed_data/order_items.csv", index=False)

# 9. Expenses
pd.DataFrame([
    {"id": 1, "restaurant_id": 1, "category": "Rent", "amount": 3000.0, "date": "2023-10-01"}
]).to_csv("seed_data/expenses.csv", index=False)

# 10. Decision Logs
pd.DataFrame([
    {
        "id": 1, 
        "restaurant_id": 1, 
        "decision_type": "supplier", 
        "inputs_json": json.dumps({"supplier": "Fresh Farms Produce", "lead_time_days": 2}),
        "chosen_option": "Accept",
        "outcome_json": json.dumps({"profit": 500.0}),
        "decided_at": "2023-09-01T10:00:00"
    }
]).to_csv("seed_data/decisions_log.csv", index=False)

print("Seed data generated.")
