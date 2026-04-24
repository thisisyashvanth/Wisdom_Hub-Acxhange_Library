from pydantic import BaseModel
from uuid import UUID
from models.request_model import RequestType, RequestStatus 
from typing import Optional
from datetime import datetime


class CreateRequestReq(BaseModel):
    book_id: UUID
    request_type: RequestType


class CreateRequestResp(BaseModel):
    id: UUID
    message: str


class ReviewRequestReq(BaseModel):
    status: RequestStatus
    remarks: Optional[str] = None


class ReviewRequestResp(BaseModel):
    id: UUID
    status: RequestStatus
    message: str


class GetRequestResp(BaseModel):
    id: UUID
    user_id: UUID
    book_id: UUID
    request_type: RequestType
    status: RequestStatus
    requested_at: datetime
    reviewed_at: Optional[datetime]
    remarks: Optional[str]

    class Config:
        from_attributes = True


class ReviewRequestBody(BaseModel):
    approve: bool
    remarks: str | None = None