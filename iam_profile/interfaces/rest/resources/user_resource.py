from pydantic import BaseModel
from datetime import datetime


class UserResource(BaseModel):
    """Resource para respuesta de usuario"""
    id: int
    email: str
    user_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True