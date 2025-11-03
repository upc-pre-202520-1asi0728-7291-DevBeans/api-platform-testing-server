from pydantic import BaseModel, Field
from datetime import date
from typing import Optional


class RegisterCoffeeLotCommand(BaseModel):
    """Command para registrar un nuevo lote de café"""
    producer_id: int
    harvest_date: date
    coffee_variety: str
    quantity: float = Field(gt=0)
    processing_method: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    altitude: Optional[float] = None
    soil_type: Optional[str] = None
    climate_zone: Optional[str] = None
    farm_section: Optional[str] = None