from pydantic import BaseModel
from datetime import date
from typing import Optional


class SearchCoffeeLotsQuery(BaseModel):
    """Query para búsqueda avanzada de lotes"""
    variety: Optional[str] = None
    processing_method: Optional[str] = None
    min_altitude: Optional[float] = None
    max_altitude: Optional[float] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None