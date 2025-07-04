from datetime import datetime
from enum import Enum
from beanie import Document, Link
from .chat import Chat


class MessageType(str, Enum):
    USER = "user"
    AI = "ai"
    HUMAN = "human"


class Message(Document):
    chat: Link[Chat]
    content: str
    timestamp: datetime = datetime.utcnow()
    message_type: MessageType = MessageType.USER  # Por defecto es mensaje de usuario
    sender_id: str | None = None  # ID del operador humano si message_type es HUMAN

    class Settings:
        name = "messages"
