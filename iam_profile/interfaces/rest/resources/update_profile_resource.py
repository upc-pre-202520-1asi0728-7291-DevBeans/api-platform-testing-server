from pydantic import BaseModel
from typing import Optional


class UpdateProfileResource(BaseModel):
    """Resource para actualizar perfil"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    farm_name: Optional[str] = None
    hectares: Optional[float] = None
    production_capacity: Optional[int] = None