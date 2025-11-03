from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class RegisterCooperativeCommand(BaseModel):
    """Command para registrar una nueva cooperativa"""
    email: EmailStr
    password: str = Field(min_length=8)
    cooperative_name: str = Field(min_length=3, max_length=255)
    legal_registration_number: str
    phone_number: str
    address: str
    city: str
    country: str = "Perú"
    legal_representative_name: str
    legal_representative_email: EmailStr
    processing_capacity: Optional[int] = None
    certifications: Optional[List[str]] = None