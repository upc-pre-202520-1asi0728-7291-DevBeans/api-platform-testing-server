from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Resource para login"""
    email: EmailStr
    password: str