from pydantic import BaseModel


class Result(BaseModel):
    rank: int
    point: int | float


class RankAndPointResponse(BaseModel):
    code: int
    result: Result
