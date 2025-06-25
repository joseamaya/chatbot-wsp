from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class BotCreate(BaseModel):
    name: str
    prompt: str
    whatsapp_phone_number_id: str
    whatsapp_token: str
    whatsapp_verify_token: str


class BotResponse(BaseModel):
    id: str
    name: str
    prompt: str
    whatsapp_phone_number_id: str
    whatsapp_verify_token: str
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
