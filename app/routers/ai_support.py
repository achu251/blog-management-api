from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import AIChat
from app.schemas import AISupportRequest, AISupportResponse
from app.services.ai_support_service import get_ai_support_response


router = APIRouter(
    prefix="/api/ai-support",
    tags=["AI Support"]
)


@router.post("/", response_model=AISupportResponse)
def ai_support(
    request: AISupportRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    user_message = request.message.strip()

    ai_response = get_ai_support_response(user_message)

    chat = AIChat(
        user_id=current_user.id,
        question=user_message,
        ai_response=ai_response,
    )

    db.add(chat)
    db.commit()

    return {
        "response": ai_response
    }
