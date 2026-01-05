from datetime import datetime
from pydantic import BaseModel

class LeaseCreateRequest(BaseModel):
    user_id: int
    equipment_id: int
    advance: int
    amount: float
    term: int
    rate: float
    payment_scheme: str | None = None


class LeaseReadResponse(BaseModel):
    id: int
    user_id: int
    equipment_id: int
    amount: float
    term: int
    rate: float
    payment_scheme: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True


class LeaseStatusUpdate(BaseModel):
    status: str
