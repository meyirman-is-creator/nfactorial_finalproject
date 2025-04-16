from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user.id"))
    message = Column(Text, nullable=False)
    response = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
