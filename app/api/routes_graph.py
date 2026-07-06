from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.restaurant import Restaurant
from app.services.build_graph import build_restaurant_graph

router = APIRouter(prefix="/api/graph", tags=["Graph"])

@router.get("/{restaurant_id}")
async def get_restaurant_graph_api(restaurant_id: int, db: Session = Depends(get_db)):
    """
    Returns a React Flow JSON payload of the restaurant's dependencies.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Restaurant with ID {restaurant_id} not found."
        )

    react_flow_payload, _ = build_restaurant_graph(restaurant_id, db)
    if not react_flow_payload:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to build graph."
        )

    return react_flow_payload
