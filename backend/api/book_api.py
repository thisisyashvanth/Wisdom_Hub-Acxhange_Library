from fastapi import APIRouter, Depends
from schemas.book_schema import CreateBookResp, CreateBookReq, GetBookResp, DeleteBookResp, GetBookUserHistoryResp, UpdateBookReq, UpdateBookResp
from security.dependency import get_current_user, require_hr
from services import book_service


router = APIRouter(prefix="/books", tags=["Book Routes"])


@router.post("/add", response_model=CreateBookResp)
def create_book(book: CreateBookReq, hr=Depends(require_hr)):
    return book_service.create_book(book)


@router.get("/get-all", response_model=list[GetBookResp])
def get_all_books(current_user=Depends(get_current_user)):
    return book_service.get_all_books()

# Pagination Version
# @router.get("/get-all")
# def get_all_books(limit: int = 10, last_key: Optional[str] = None, current_user=Depends(get_current_user)):
#     parsed_key = json.loads(last_key) if last_key else None
#     return book_service.get_all_books(limit, parsed_key)


@router.get("/get/{id}", response_model=GetBookResp)
def get_book(id: str, current_user=Depends(get_current_user)):
    return book_service.get_book(id)


@router.delete("/remove/{id}", response_model=DeleteBookResp)
def delete_book(id: str, hr=Depends(require_hr)):
    return book_service.delete_book(id)


@router.put("/update/{id}", response_model=UpdateBookResp)
def update_book(id: str, book: UpdateBookReq, hr=Depends(require_hr)):
    return book_service.update_book(id, book)


@router.get("/{id}/users", response_model=list[GetBookUserHistoryResp])
def get_book_user_history(id: str, hr=Depends(require_hr)):
    return book_service.get_book_user_history(id)