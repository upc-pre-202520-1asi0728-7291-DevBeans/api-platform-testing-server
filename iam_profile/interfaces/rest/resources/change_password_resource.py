from pydantic import BaseModel, Field


class ChangePasswordResource(BaseModel):
    """Resource para cambiar contraseña"""
    current_password: str
    new_password: str = Field(min_length=8)