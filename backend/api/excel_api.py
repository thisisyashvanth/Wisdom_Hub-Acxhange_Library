from fastapi import APIRouter, Depends
from security.dependency import require_hr
from fastapi.responses import StreamingResponse
from utils.excel_utility import (generate_book_history_excel, generate_books_excel, generate_requests_excel, generate_users_excel)


router = APIRouter(prefix="/hr", tags=["Excel Routes"])


@router.post("/export-users")
def export_users(users: list[dict], hr=Depends(require_hr)):
    return StreamingResponse(
        generate_users_excel(users),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=users.xlsx"},
    )


@router.post("/export-requests")
def export_requests(requests: list[dict], hr=Depends(require_hr)):
    return StreamingResponse(
        generate_requests_excel(requests),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=request_history.xlsx"},
    )


@router.post("/export-books")
def export_books(books: list[dict], hr=Depends(require_hr)):
    return StreamingResponse(
        generate_books_excel(books),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=available_books.xlsx"},
    )


@router.post("/export-book-history")
def export_book_history(history: list[dict], hr=Depends(require_hr)):
    return StreamingResponse(
        generate_book_history_excel(history),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=book_history.xlsx"},
    )