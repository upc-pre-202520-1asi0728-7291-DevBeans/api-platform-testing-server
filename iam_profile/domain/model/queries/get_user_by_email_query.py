from pydantic import BaseModel


class GetUserByEmailQuery(BaseModel):
    email: str