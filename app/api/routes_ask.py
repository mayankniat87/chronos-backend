import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.menu_ai.assistant import ask_menu_assistant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ask", tags=["Ask AI"])


class AskRequest(BaseModel):
    restaurant_id: int
    question: str = Field(min_length=1, max_length=500)
    # Lets the frontend keep a per-chat memory thread; any stable string works.
    session_id: str = Field(default="default", max_length=100)


class AskResponse(BaseModel):
    answer: str
    matched_item_ids: list[int]
    out_of_menu: bool
    grounded: bool


@router.post("", response_model=AskResponse)
async def ask_ai(request: AskRequest, db: Session = Depends(get_db)):
    """Grounded menu Q&A: answers only from the restaurant's actual menu."""
    try:
        result = ask_menu_assistant(
            db=db,
            restaurant_id=request.restaurant_id,
            question=request.question,
            session_id=request.session_id,
        )
        return AskResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        logger.exception("Ask AI request failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The assistant is temporarily unavailable. Please try again.",
        )
