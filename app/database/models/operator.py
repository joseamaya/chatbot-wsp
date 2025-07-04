from datetime import datetime
from beanie import Document
from pydantic import EmailStr


class Operator(Document):
    email: EmailStr
    hashed_password: str
    full_name: str
    is_active: bool = True
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "operators"
