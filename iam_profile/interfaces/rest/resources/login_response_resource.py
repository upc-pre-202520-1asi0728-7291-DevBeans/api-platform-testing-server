from pydantic import BaseModel
from iam_profile.interfaces.rest.resources.user_resource import UserResource


class LoginResponse(BaseModel):
    """Resource para respuesta de login"""
    access_token: str
    token_type: str
    user: UserResource