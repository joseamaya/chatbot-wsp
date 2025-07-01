from datetime import datetime
from typing import Optional, List
from beanie import Document, Indexed


class Bot(Document):
    name: Indexed(str, unique=True)
    prompt: str
    whatsapp_phone_number_id: str
    whatsapp_token: str
    whatsapp_verify_token: str
    welcome_message: Optional[str] = None

    # Contact and location information
    business_hours: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None

    # Social media
    tiktok: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    website: Optional[str] = None

    # Business information
    specialties: List[str] = []
    payment_methods: List[str] = []
    prices: List[str] = []

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
                "welcome_message": "Hello! How can I help you?",
                "business_hours": "Monday to Friday from 9:00 AM to 6:00 PM",
                "address": "123 Example Ave, City",
                "phone": "+51987654321",
                "tiktok": "@example",
                "facebook": "facebook.com/example",
                "instagram": "@example",
                "website": "www.example.com",
                "specialties": ["Specialty 1", "Specialty 2"],
                "payment_methods": ["Cash", "Credit Card", "Bank Transfer"],
                "prices": ["Service 1 - $100", "Service 2 - $200"],
                "is_active": True
            }
        }
