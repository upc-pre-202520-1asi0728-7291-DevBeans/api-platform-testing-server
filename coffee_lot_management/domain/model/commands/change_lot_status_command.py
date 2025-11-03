from pydantic import BaseModel
from typing import Optional


class ChangeLotStatusCommand(BaseModel):
    """Command para cambiar estado de un lote"""
    lot_id: int
    new_status: str
    change_reason: Optional[str] = None