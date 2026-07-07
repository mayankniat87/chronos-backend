from sqlalchemy.orm import Session
from app.services.simulation.scenario_generator import generate_scenarios
from app.services.simulation.confidence_calculator import calculate_confidence
from app.services.simulation.explain import explain_decision
from app.schemas.restaurant import DecisionSimulationResponse, ScenarioResponse
from app.models.restaurant import SimulationRun
import logging

logger = logging.getLogger(__name__)

def process_decision_simulation(restaurant_id: int, question: str, decision_type: str, params: dict, db: Session) -> DecisionSimulationResponse:
    logger.info(
    f"Running simulation for restaurant_id={restaurant_id}, decision_type={decision_type}"
    )
    
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
            db.refresh(run_record)

            logger.info(
                f"Simulation saved successfully (id={run_record.id})"
            )
        except Exception:
            db.rollback()
            logger.exception(
                "Could not persist simulation log."
            )
            
        return response
    except Exception:
        logger.exception(
            "Error while processing decision simulation."
        )
        fallback = get_fallback_simulation(restaurant_id, db)
        if fallback:
            return fallback
        raise 

def get_fallback_simulation(restaurant_id: int, db: Session):
    run = db.query(SimulationRun).filter(SimulationRun.restaurant_id == restaurant_id).order_by(SimulationRun.created_at.desc()).first()
    if run:
        scenarios = [ScenarioResponse(**s) for s in run.scenarios_json]
        logger.warning(
            f"Loaded fallback simulation for restaurant {restaurant_id}"
        )
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
    logger.error(
        f"No fallback simulation found for restaurant {restaurant_id}"
    )

    return None
