from sqlalchemy.orm import Session
from app.services.simulation.scenario_generator import generate_scenarios
from app.services.simulation.confidence_calculator import calculate_confidence
from app.services.simulation.explain import explain_decision
from app.schemas.restaurant import DecisionSimulationResponse, ScenarioResponse
from app.models.restaurant import SimulationRun
import logging

def process_decision_simulation(restaurant_id: int, question: str, decision_type: str, params: dict, db: Session) -> DecisionSimulationResponse:
    try:
        # 1. Generate deterministic scenarios
        scenarios = generate_scenarios(restaurant_id, decision_type, params, db)
        
        # 2. Calculate deterministic confidence
        confidence = calculate_confidence(scenarios)
        
        # 3. Minimal Graph Context for LLM
        graph_context = {
            "affected_nodes": ["staff", "revenue", "cost"] if decision_type == "hire" else ["inventory", "supplier", "revenue", "cost"],
            "decision_type": decision_type
        }
        
        # 4. LLM Explanation
        llm_output = explain_decision(question, scenarios, graph_context)
        
        # 5. Build response
        scenario_responses = [ScenarioResponse(**s) for s in scenarios]
        
        response = DecisionSimulationResponse(
            restaurant_id=restaurant_id,
            question=question,
            decision_type=decision_type,
            scenarios=scenario_responses,
            recommendation=llm_output.get("recommendation", "Proceed with caution."),
            confidence=confidence,
            causal_explanation=llm_output.get("causal_explanation", "No causal chain provided."),
            graph_payload=graph_context
        )
        
        # 6. Save to simulation_runs
        try:
            run_record = SimulationRun(
                restaurant_id=restaurant_id,
                question_text=question,
                scenarios_json=[s.model_dump() for s in scenario_responses],
                recommendation=response.recommendation,
                confidence=confidence
            )
            db.add(run_record)
            db.commit()
        except Exception as e:
            db.rollback()
            logging.warning(f"Could not persist simulation log: {e}")
            
        return response
    except Exception as e:
        logging.error(f"Error in process_decision_simulation: {e}")
        fallback = get_fallback_simulation(restaurant_id, db)
        if fallback:
            return fallback
        raise e

def get_fallback_simulation(restaurant_id: int, db: Session):
    run = db.query(SimulationRun).filter(SimulationRun.restaurant_id == restaurant_id).order_by(SimulationRun.created_at.desc()).first()
    if run:
        scenarios = [ScenarioResponse(**s) for s in run.scenarios_json]
        return DecisionSimulationResponse(
            restaurant_id=restaurant_id,
            question=run.question_text,
            decision_type="fallback",
            scenarios=scenarios,
            recommendation=run.recommendation,
            confidence=run.confidence,
            causal_explanation="(Loaded from past fallback due to error in processing)",
            graph_payload={}
        )
    return None
