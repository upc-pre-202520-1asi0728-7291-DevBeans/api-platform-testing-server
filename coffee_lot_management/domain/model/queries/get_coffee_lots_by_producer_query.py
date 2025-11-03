from pydantic import BaseModel
from typing import Optional


class GetCoffeeLotsByProducerQuery(BaseModel):
    """Query para obtener lotes de un productor"""
    producer_id: int
    status: Optional[str] = None
    harvest_year: Optional[int] = None