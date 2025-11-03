from pydantic import BaseModel, Field


class ChangePasswordCommand(BaseModel):
    """Command para cambiar contraseña"""
    user_id: int
    current_password: str
    new_password: str = Field(min_length=8)