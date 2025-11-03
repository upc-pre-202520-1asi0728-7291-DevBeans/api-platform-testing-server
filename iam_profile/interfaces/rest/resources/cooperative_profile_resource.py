from pydantic import BaseModel
from typing import Optional, List


class CooperativeProfileResource(BaseModel):
    """Resource para perfil de cooperativa"""
    id: int
    user_id: int
    cooperative_name: str
    legal_registration_number: str
    phone_number: str
    address: str
    city: str
    country: str
    legal_representative_name: str
    legal_representative_email: str
    processing_capacity: Optional[int]
    certifications: Optional[List[str]]

    class Config:
        from_attributes = True