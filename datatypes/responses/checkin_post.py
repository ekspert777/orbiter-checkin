from typing import Optional

from pydantic import BaseModel


class CheckinPostResponse(BaseModel):
    code: int
    result: Optional[str] = None
    message: Optional[str] = None
