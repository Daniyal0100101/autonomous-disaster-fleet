from pydantic import BaseModel


class Robot(BaseModel):
    id: str
    status: str
