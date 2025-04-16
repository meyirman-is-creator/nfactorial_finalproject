from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.chatbot import ChatMessageCreate, ChatResponse
from app.crud.chatbot import chatbot

router = APIRouter()

@router.post("/send", response_model=ChatResponse)
def send_message(message_data: ChatMessageCreate, db: Session = Depends(get_db)):
    # Сохраняем сообщение в базу данных
    user_message = chatbot.create_message(db=db, obj_in=message_data)

    # Здесь может быть логика ответа ИИ. Пока просто заглушка:
    ai_response = f"Echo: {user_message.message}"

    # Обновим сообщение с ответом
    user_message.response = ai_response
    db.commit()
    db.refresh(user_message)

    return {"message": ai_response}
