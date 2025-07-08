from datetime import datetime, UTC
from beanie import Document, Link
from pydantic import Field
from .bot import Bot


class Chat(Document):
    phone_number: str
    bot: Link[Bot]
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_interaction: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    context: dict = {}
    messages_count: int = 0
    needs_human_support: bool = False

    class Settings:
        name = "chats"
