from pydantic import BaseModel, Field
from typing import Optional


class UpdateCoffeeLotCommand(BaseModel):
    """Command para actualizar un lote existente"""
    lot_id: int
    quantity: Optional[float] = Field(gt=0, default=None)
    processing_method: Optional[str] = None
    altitude: Optional[float] = None
    soil_type: Optional[str] = None
    climate_zone: Optional[str] = None