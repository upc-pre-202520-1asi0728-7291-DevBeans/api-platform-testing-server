from pydantic import BaseModel
from typing import Optional, List


class ProducerProfileResource(BaseModel):
    """Resource para perfil de productor"""
    id: int
    user_id: int
    first_name: str
    last_name: str
    document_number: str
    document_type: str
    phone_number: str
    city: str
    country: str
    farm_name: str
    latitude: float
    longitude: float
    altitude: Optional[float]
    region: str
    hectares: float
    coffee_varieties: Optional[List[str]]
    production_capacity: Optional[int]

    class Config:
        from_attributes = True