from pydantic import BaseModel


class Result(BaseModel):
    addressCount: int


class LeaderboardInfoResponse(BaseModel):
    code: int
    result: Result
