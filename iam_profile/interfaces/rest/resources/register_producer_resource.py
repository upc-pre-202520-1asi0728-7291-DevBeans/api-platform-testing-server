from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class RegisterProducerResource(BaseModel):
    """Resource para registro de productor"""
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = Field(min_length=2, max_length=100)
    last_name: str = Field(min_length=2, max_length=100)
    document_number: str
    document_type: str
    phone_number: str
    city: str
    country: str = "Perú"
    farm_name: str = Field(min_length=3, max_length=200)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude: Optional[float] = None
    region: str
    hectares: float = Field(gt=0)
    coffee_varieties: Optional[List[str]] = None
    production_capacity: Optional[int] = None