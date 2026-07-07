from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.models.restaurant import Restaurant, Supplier, InventoryItem, MenuItem, Staff

def evaluate_decision(restaurant_id: int, decision_type: str, params: Dict[str, Any], demand_multiplier: float, db: Session) -> Dict[str, Any]:
    """
    Evaluates a decision using deterministic domain rules and returns metrics.
    
    demand_multiplier allows the Scenario Generator to simulate Optimistic (e.g. 1.15), 
    Likely (1.0), and Pessimistic (0.85) conditions.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise ValueError("Restaurant not found")

    metrics = {
        "revenue": 0.0,
        "cost": 0.0,
        "profit": 0.0,
        "risk_level": "low",
        "flags": [],
        "metrics": {}
    }

    # Baseline daily revenue & cost (simplified)
    # E.g., average spend per customer * visit count / 30 days
    base_daily_revenue = sum(c.avg_spend * (c.visit_count / 30.0) for c in restaurant.customers) if restaurant.customers else 500.0
    
    # Base daily cost
    # Staff cost
    daily_staff_cost = sum(s.hourly_cost * (s.weekly_hours / 7.0) for s in restaurant.staff) if restaurant.staff else 200.0
    # Inventory cost roughly 30% of revenue
    base_daily_cost = daily_staff_cost + (base_daily_revenue * 0.3)
    cost_multiplier = params.get("cost_multiplier", 1.0)
    base_daily_cost *= cost_multiplier
    base_profit = base_daily_revenue - base_daily_cost

    # 1. HIRE DECISION
    if decision_type == "hire":
        role = params.get("role", "chef")
        hourly_rate = params.get("hourly_rate", 20.0)
        hours = params.get("hours", 40.0)
        
        added_cost = (hourly_rate * hours) / 7.0 # daily
        
        # Hiring a chef increases capacity, allowing demand multiplier to be realized fully
        # If pessimistic, demand doesn't increase but cost does.
        new_revenue = base_daily_revenue * demand_multiplier
        new_cost = base_daily_cost + added_cost
        
        metrics["revenue"] = new_revenue * 30 # monthly projection
        metrics["cost"] = new_cost * 30
        metrics["profit"] = (new_revenue - new_cost) * 30
        
        if demand_multiplier < 1.0:
            metrics["risk_level"] = "high"
            metrics["flags"].append("Fixed labor cost increases while demand drops.")
        else:
            metrics["risk_level"] = "low"
            
        metrics["metrics"]["staff_utilization"] = f"{int(80 / demand_multiplier)}%"

    # 2. SUPPLIER DECISION
    elif decision_type == "supplier":
        new_lead_time = params.get("lead_time_days", 2)
        reliability = params.get("reliability_score", 0.9)
        cost_savings_pct = params.get("cost_savings_pct", 0.10)
        
        # Inventory cost drops
        inventory_cost = (base_daily_revenue * 0.3) * (1 - cost_savings_pct)
        
        # If supplier is unreliable, revenue takes a hit due to stockouts
        effective_reliability = reliability * demand_multiplier # pessimistic reduces reliability
        revenue_hit = 1.0 if effective_reliability > 0.8 else 0.85
        
        new_revenue = base_daily_revenue * revenue_hit
        new_cost = daily_staff_cost + inventory_cost
        
        metrics["revenue"] = new_revenue * 30
        metrics["cost"] = new_cost * 30
        metrics["profit"] = (new_revenue - new_cost) * 30
        
        if effective_reliability < 0.75:
            metrics["risk_level"] = "high"
            metrics["flags"].append("High risk of stockouts due to poor supplier reliability.")
        elif effective_reliability < 0.9:
            metrics["risk_level"] = "medium"
        else:
            metrics["risk_level"] = "low"
            
        metrics["metrics"]["inventory_wastage"] = f"{round((1 - effective_reliability) * 10, 1)}%"

    # 3. CATERING / BULK ORDER
    elif decision_type == "catering":
        order_value = params.get("order_value", 2000.0)
        order_complexity = params.get("complexity_score", 1.5) # 1.0 is normal
        
        # This is a one-off event. Let's do a 7-day projection.
        new_revenue = (base_daily_revenue * 7) + (order_value * demand_multiplier)
        
        # Cost to fulfill
        added_cogs = order_value * 0.4
        
        # Staff hours vs order complexity constraint
        total_weekly_hours = sum(s.weekly_hours for s in restaurant.staff) if restaurant.staff else 100.0
        required_hours = 100.0 * order_complexity
        
        overtime_cost = 0.0
        if required_hours > total_weekly_hours:
            overtime_hours = required_hours - total_weekly_hours
            overtime_cost = overtime_hours * 30.0 # $30/hr overtime
            metrics["flags"].append(f"Requires {overtime_hours} hours of overtime.")
            metrics["risk_level"] = "medium"
            if overtime_hours > 50:
                metrics["risk_level"] = "high"
                metrics["flags"].append("Severe staff strain. High risk of delayed fulfillment.")
                
        new_cost = (base_daily_cost * 7) + added_cogs + overtime_cost
        
        metrics["revenue"] = new_revenue
        metrics["cost"] = new_cost
        metrics["profit"] = new_revenue - new_cost
        metrics["metrics"]["customer_wait_time_change"] = (
        "+5 mins" if metrics["risk_level"] == "high" else "+1 mins")

    else:
        # Generic decision
        metrics["revenue"] = base_daily_revenue * 30 * demand_multiplier
        metrics["cost"] = base_daily_cost * 30
        metrics["profit"] = metrics["revenue"] - metrics["cost"]

    # Ensure clean float rounding
    metrics["revenue"] = round(metrics["revenue"], 2)
    metrics["cost"] = round(metrics["cost"], 2)
    metrics["profit"] = round(metrics["profit"], 2)

    return metrics
