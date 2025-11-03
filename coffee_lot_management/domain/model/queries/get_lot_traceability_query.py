from pydantic import BaseModel


class GetLotTraceabilityQuery(BaseModel):
    """Query para información completa de trazabilidad"""
    lot_number: str