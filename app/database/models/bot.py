from datetime import datetime
from typing import Optional

from beanie import Document, Indexed


class Bot(Document):
    name: Indexed(str, unique=True)
    prompt: str
    whatsapp_phone_number_id: str
    whatsapp_token: str
    whatsapp_verify_token: str
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None
    is_active: bool = True

    class Settings:
        name = "bots"

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Bot",
                "prompt": "You are a helpful assistant...",
                "whatsapp_phone_number_id": "123456789",
                "whatsapp_token": "EAARY...",
                "whatsapp_verify_token": "chatbot_wsp",
                "is_active": True
            }
        }
