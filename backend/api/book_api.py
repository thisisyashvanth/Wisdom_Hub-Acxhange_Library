from fastapi import APIRouter, Depends
from schemas.book_schema import CreateBookResp, CreateBookReq, GetBookResp, DeleteBookResp , GetBookUserHistoryResp
from security.dependency import get_current_user, require_hr
from services import book_service


router = APIRouter(prefix="/books", tags=["Book Routes"])


@router.post("/add", response_model=CreateBookResp)
def create_book(book: CreateBookReq, hr=Depends(require_hr)):
    return book_service.create_book(book)


@router.get("/get-all", response_model=list[GetBookResp])
def get_all_books(current_user=Depends(get_current_user)):
    return book_service.get_all_books()


@router.get("/get/{id}", response_model=GetBookResp)
def get_book(id: str, current_user=Depends(get_current_user)):
    return book_service.get_book(id)


@router.delete("/remove/{id}", response_model=DeleteBookResp)
def delete_book(id: str, hr=Depends(require_hr)):
    return book_service.delete_book(id)


@router.get("/{id}/users", response_model=list[GetBookUserHistoryResp])
def get_book_user_history(id: str, hr=Depends(require_hr)):
    return book_service.get_book_user_history(id)