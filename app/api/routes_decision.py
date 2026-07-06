from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.core.database import get_db
from app.models.restaurant import Restaurant, DecisionLog, SimulationRun
from app.schemas.restaurant import DecisionSimulationResponse, ScenarioResponse

router = APIRouter(prefix="/api/decisions", tags=["Decisions"])

from app.services.decision_service import process_decision_simulation
from app.schemas.restaurant import DecisionSimulationRequest

@router.post("/simulate", response_model=DecisionSimulationResponse)
async def simulate_decision(
    request: DecisionSimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Simulates a business decision across three future timelines (Optimistic, Likely, Pessimistic).
    """
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == request.restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant with ID {request.restaurant_id} not found."
        )

    response = process_decision_simulation(
        restaurant_id=request.restaurant_id,
        question=request.question,
        decision_type=request.decision_type,
        params=request.params,
        db=db
    )
    
    return response


@router.get("/history/{restaurant_id}")
async def get_decision_history(restaurant_id: int, db: Session = Depends(get_db)):
    """
    Fetches the history of past decisions made (Decision Memory) for the restaurant.
    This reads from the real 'decisions_log' table in the database.
    """
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant with ID {restaurant_id} not found."
        )

    history = db.query(DecisionLog).filter(DecisionLog.restaurant_id == restaurant_id).order_by(DecisionLog.decided_at.desc()).all()
    
    return {
        "status": "success",
        "restaurant_id": restaurant_id,
        "history": [
            {
                "id": item.id,
                "decision_type": item.decision_type,
                "inputs_json": item.inputs_json,
                "chosen_option": item.chosen_option,
                "outcome_json": item.outcome_json,
                "decided_at": item.decided_at.isoformat()
            }
            for item in history
        ]
    }


@router.get("/simulations/{restaurant_id}")
async def get_simulation_history(restaurant_id: int, db: Session = Depends(get_db)):
    """
    Fetches the history of past simulation runs for the restaurant.
    """
    # Verify restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant with ID {restaurant_id} not found."
        )

    runs = db.query(SimulationRun).filter(SimulationRun.restaurant_id == restaurant_id).order_by(SimulationRun.created_at.desc()).all()
    
    return {
        "status": "success",
        "restaurant_id": restaurant_id,
        "runs": [
            {
                "id": run.id,
                "question": run.question_text,
                "scenarios": run.scenarios_json,
                "recommendation": run.recommendation,
                "confidence": run.confidence,
                "created_at": run.created_at.isoformat()
            }
            for run in runs
        ]
    }

