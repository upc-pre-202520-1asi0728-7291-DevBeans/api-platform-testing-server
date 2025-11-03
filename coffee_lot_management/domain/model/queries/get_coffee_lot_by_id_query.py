from pydantic import BaseModel


class GetCoffeeLotByIdQuery(BaseModel):
    """Query para obtener lote por ID"""
    lot_id: int