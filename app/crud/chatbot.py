import uuid
from sqlalchemy.orm import Session
from app.models.chatbot import ChatMessage
from app.schemas.chatbot import ChatMessageCreate


class CRUDChatbot:
    def create_message(self, db: Session, *, obj_in: ChatMessageCreate) -> ChatMessage:
        chat_id = str(uuid.uuid4())
        db_obj = ChatMessage(
            id=chat_id,
            user_id=obj_in.user_id,
            message=obj_in.message,
            response=obj_in.response,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


chatbot = CRUDChatbot()
