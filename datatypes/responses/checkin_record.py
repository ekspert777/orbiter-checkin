from typing import List, Optional

from pydantic import BaseModel


class CheckInRecord(BaseModel):
    date: Optional[str]
    chainId: Optional[str]
    opoint: Optional[int]


class Result(BaseModel):
    checkInRecords: List[CheckInRecord]
    totalCount: int
    checkInRewards: List[dict]
    checkInCount: int


class CheckinRecordResponse(BaseModel):
    code: int
    result: Result
