from pydantic import BaseModel


class GetCooperativeProfileQuery(BaseModel):
    user_id: int