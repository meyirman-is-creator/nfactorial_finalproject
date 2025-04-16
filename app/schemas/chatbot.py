from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatMessageCreate(BaseModel):
    user_id: str
    message: str
    response: Optional[str] = None


class ChatMessageOut(BaseModel):
    id: str
    user_id: str
    message: str
    response: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class ChatMessage(BaseModel):
    id: str
    user_id: str
    message: str
    response: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class ChatResponse(BaseModel):
    message: str
