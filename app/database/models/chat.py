from datetime import datetime
from typing import Optional
from beanie import Document, Link
from .bot import Bot


class Chat(Document):
    phone_number: str
    bot: Link[Bot]
    started_at: datetime = datetime.utcnow()
    last_interaction: datetime = datetime.utcnow()
    is_active: bool = True
    context: dict = {}
    messages_count: int = 0

    class Settings:
        name = "chats"
