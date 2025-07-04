from pydantic import BaseModel, EmailStr


class OperatorCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str


class OperatorLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
