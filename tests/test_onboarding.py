import io
import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup system path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base
from app.models.restaurant import (
    Restaurant, Supplier, MenuItem, InventoryItem, 
    Staff, Customer, Order, OrderItem, Expense, DecisionLog
)
from app.api.routes_upload import import_table_data

def create_mock_excel_file() -> bytes:
    """Generates an Excel workbook with sheets mapping to the SQL schemas."""
    output = io.BytesIO()
    
    # Define simple mock records
    df_restaurants = pd.DataFrame([{
        "id": 1,
        "name": "La Piazza",
        "cuisine_type": "Italian",
        "cash_balance": 50000.0
    }])
    
    df_suppliers = pd.DataFrame([{
        "id": 10,
        "restaurant_id": 1,
        "name": "Fresh Farms Ltd",
        "reliability_score": 0.95,
        "avg_lead_time_days": 2.0
    }])
    
    df_menu_items = pd.DataFrame([{
        "id": 100,
        "restaurant_id": 1,
        "name": "Margherita Pizza",
        "category": "Mains",
        "cost_price": 4.50,
        "sell_price": 12.00
    }])
    
    df_inventory = pd.DataFrame([{
        "id": 1000,
        "restaurant_id": 1,
        "menu_item_id": 100,
        "supplier_id": 10,
        "stock_qty": 50.0,
        "reorder_level": 10.0,
        "storage_capacity": 200.0
    }])
    
    df_staff = pd.DataFrame([{
        "id": 20,
        "restaurant_id": 1,
        "role": "Sous Chef",
        "weekly_hours": 40.0,
        "hourly_cost": 25.0,
        "shift_pattern": "Morning"
    }])
    
    df_customers = pd.DataFrame([{
        "id": 30,
        "restaurant_id": 1,
        "name": "Alice Smith",
        "visit_count": 12,
        "avg_spend": 45.0,
        "churn_flag": "False" # Tested as string conversion
    }])
    
    df_orders = pd.DataFrame([{
        "id": 50,
        "restaurant_id": 1,
        "customer_id": 30,
        "type": "regular",
        "value": 45.0,
        "date": "2026-07-01",
        "status": "completed"
    }])
    
    df_order_items = pd.DataFrame([{
        "id": 500,
        "order_id": 50,
        "menu_item_id": 100,
        "qty": 2.0,
        "price_at_order": 12.0
    }])
    
    df_expenses = pd.DataFrame([{
        "id": 60,
        "restaurant_id": 1,
        "category": "Rent",
        "amount": 2000.0,
        "date": "2026-07-01"
    }])
    
    df_decisions = pd.DataFrame([{
        "id": 70,
        "restaurant_id": 1,
        "decision_type": "hire",
        "inputs_json": '{"role": "Chef", "hours": 40}',
        "chosen_option": "Yes",
        "outcome_json": '{"impact": "high"}',
        "decided_at": "2026-07-01T12:00:00"
    }])
    
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_restaurants.to_excel(writer, sheet_name="restaurants", index=False)
        df_suppliers.to_excel(writer, sheet_name="suppliers", index=False)
        df_menu_items.to_excel(writer, sheet_name="menu_items", index=False)
        df_inventory.to_excel(writer, sheet_name="inventory_items", index=False)
        df_staff.to_excel(writer, sheet_name="staff", index=False)
        df_customers.to_excel(writer, sheet_name="customers", index=False)
        df_orders.to_excel(writer, sheet_name="orders", index=False)
        df_order_items.to_excel(writer, sheet_name="order_items", index=False)
        df_expenses.to_excel(writer, sheet_name="expenses", index=False)
        df_decisions.to_excel(writer, sheet_name="decisions_log", index=False)
        
    return output.getvalue()

def run_tests():
    print("Testing Chronos Backend Core schemas and upload logic...")
    
    # 1. Setup in-memory test database
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    try:
        # 2. Excel Data Import Simulation
        print("Creating mock Excel workbook...")
        excel_bytes = create_mock_excel_file()
        excel_file = pd.ExcelFile(io.BytesIO(excel_bytes))
        
        # Mapping definition
        mappings = {
            "restaurants": Restaurant,
            "suppliers": Supplier,
            "menu_items": MenuItem,
            "inventory_items": InventoryItem,
            "staff": Staff,
            "customers": Customer,
            "orders": Order,
            "order_items": OrderItem,
            "expenses": Expense,
            "decisions_log": DecisionLog,
        }
        
        print("Importing sheets...")
        for key, model_cls in mappings.items():
            df = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=key)
            rows = import_table_data(
                model_name=key,
                model_cls=model_cls,
                df=df,
                db=db,
                clear_existing=True
            )
            print(f"  - Imported {rows} records into {key}")
            
        # 3. Assertions and Queries
        print("Running database queries validation...")
        
        restaurant = db.query(Restaurant).first()
        assert restaurant is not None
        assert restaurant.name == "La Piazza"
        print("  [PASSED] Restaurant record created correctly.")
        
        supplier = db.query(Supplier).first()
        assert supplier.name == "Fresh Farms Ltd"
        assert supplier.reliability_score == 0.95
        print("  [PASSED] Supplier record verified.")
        
        menu_item = db.query(MenuItem).first()
        assert menu_item.name == "Margherita Pizza"
        assert menu_item.cost_price == 4.5
        print("  [PASSED] Menu Item record verified.")
        
        inventory = db.query(InventoryItem).first()
        assert inventory.stock_qty == 50.0
        assert inventory.menu_item_id == menu_item.id
        print("  [PASSED] Inventory Item relations verified.")
        
        order = db.query(Order).first()
        assert order.value == 45.0
        assert str(order.date) == "2026-07-01"
        print("  [PASSED] Order and date conversions verified.")
        
        decision = db.query(DecisionLog).first()
        assert decision.decision_type == "hire"
        assert isinstance(decision.inputs_json, dict)
        assert decision.inputs_json["role"] == "Chef"
        print("  [PASSED] Decision Log JSON parsing verified.")
        
        print("\nAll database schema and onboarding parser tests PASSED successfully!")
        
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

if __name__ == "__main__":
    run_tests()
