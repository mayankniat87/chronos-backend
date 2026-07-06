from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.services.simulation.rule_engine import evaluate_decision

def generate_scenarios(restaurant_id: int, decision_type: str, params: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
    """
    Runs the deterministic rule engine thrice to produce 3 timelines (optimistic, likely, pessimistic).
    """
    
    # 1. Optimistic: Demand is 15% higher
    optimistic = evaluate_decision(restaurant_id, decision_type, params, demand_multiplier=1.15, db=db)
    optimistic["name"] = "optimistic"
    
    # 2. Likely: Expected demand
    likely = evaluate_decision(restaurant_id, decision_type, params, demand_multiplier=1.0, db=db)
    likely["name"] = "likely"
    
    # 3. Pessimistic: Demand is 15% lower
    pessimistic = evaluate_decision(restaurant_id, decision_type, params, demand_multiplier=0.85, db=db)
    pessimistic["name"] = "pessimistic"
    
    return [optimistic, likely, pessimistic]
