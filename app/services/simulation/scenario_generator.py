from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.services.simulation.rule_engine import evaluate_decision

def generate_scenarios(restaurant_id: int, decision_type: str, params: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
    """
    Runs the deterministic rule engine thrice to produce 3 timelines (optimistic, likely, pessimistic).
    """
    
    # 1. Optimistic: Demand is 15% higher
    optimistic_params = params.copy()
    optimistic_params["cost_multiplier"] = 0.97

    optimistic = evaluate_decision(
        restaurant_id,
        decision_type,
        optimistic_params,
        demand_multiplier=1.15,
        db=db
    )
    optimistic["name"] = "optimistic"
    
    # 2. Likely: Expected demand
    likely_params = params.copy()
    likely_params["cost_multiplier"] = 1.0

    likely = evaluate_decision(
        restaurant_id,
        decision_type,
        likely_params,
        demand_multiplier=1.0,
        db=db
    )
    likely["name"] = "likely"

    # 3. Pessimistic: Demand is 15% lower
    pessimistic_params = params.copy()
    pessimistic_params["cost_multiplier"] = 1.05

    pessimistic = evaluate_decision(
        restaurant_id,
        decision_type,
        pessimistic_params,
        demand_multiplier=0.85,
        db=db
    )
    pessimistic["name"] = "pessimistic"

    if pessimistic["risk_level"] == "low":
        pessimistic["risk_level"] = "medium"

    return [optimistic, likely, pessimistic]
