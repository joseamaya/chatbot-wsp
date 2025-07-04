from datetime import datetime
from beanie import Document, Link
from .chat import Chat


class Message(Document):
    chat: Link[Chat]
    content: str
    timestamp: datetime = datetime.utcnow()
    
    class Settings:
        name = "messages"
