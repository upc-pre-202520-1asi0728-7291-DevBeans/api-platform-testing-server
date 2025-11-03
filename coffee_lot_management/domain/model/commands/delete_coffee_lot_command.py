from pydantic import BaseModel


class DeleteCoffeeLotCommand(BaseModel):
    """Command para eliminar un lote"""
    lot_id: int
    deletion_reason: str