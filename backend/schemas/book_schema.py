from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class CreateBookResp(BaseModel):
    title: str
    bookNumber: str
    author: str
    isbn: str
    category: str | None = None
    total_copies: int
    available_copies: int

    model_config = {
        "from_attributes": True
    }


class CreateBookReq(BaseModel):
    title: str
    author: str
    bookNumber: str
    isbn: str
    category: str
    total_copies: int


class GetBookResp(BaseModel):
    id: UUID
    title: str
    bookNumber: str
    author: str
    isbn: str
    category: str
    total_copies: int
    available_copies: int

    model_config = {
        "from_attributes": True
    }


class DeleteBookResp(BaseModel):
    title: str
    response: str

    model_config = {
        "from_attributes": True
    }


class GetBookUserHistoryResp(BaseModel):
    borrow_id: UUID
    user_id: UUID
    employee_id: str
    employee_name: str
    issue_date: datetime
    due_date: datetime
    returned_date: Optional[datetime]
    status: str
    renewal_count: int
    
    model_config = {
        "from_attributes": True
    }


class GetBasicBook(BaseModel):
    id: UUID
    title: str
    author: str
    category: str | None

    model_config = {"from_attributes": True}