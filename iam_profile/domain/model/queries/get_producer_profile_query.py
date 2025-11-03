from pydantic import BaseModel


class GetProducerProfileQuery(BaseModel):
    user_id: int