from pydantic import BaseModel


class AccItem(BaseModel):
    index: int
    private_key: str
