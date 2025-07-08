from datetime import datetime, UTC
from enum import Enum
from beanie import Document, Link
from pydantic import Field
from .chat import Chat


class MessageType(str, Enum):
    USER = "user"
    AI = "ai"
    HUMAN = "human"


class Message(Document):
    chat: Link[Chat]
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    message_type: MessageType = MessageType.USER
    sender_id: str | None = None

    class Settings:
        name = "messages"
