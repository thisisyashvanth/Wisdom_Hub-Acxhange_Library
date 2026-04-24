from models import borrow_model, user_model
from models.book_model import get_book_by_id
from schemas.user_schema import GetUserBooksResp, GetUserHistoryResp
from fastapi import HTTPException
from schemas.book_schema import GetBasicBook


def get_my_books(current_user: dict):
    records = borrow_model.get_borrows_by_user(current_user["id"])
    result = []

    for r in records:
        book = get_book_by_id(r["book_id"])
        result.append(
            GetUserBooksResp(
                borrow_id=r["id"],
                book_id=r["book_id"],
                book_title=book["title"] if book else "Unknown",
                issue_date=r["issue_date"],
                due_date=r["due_date"],
                returned_date=r.get("returned_date"),
                status=r["status"],
                renewal_count=int(r.get("renewal_count", 0)),
            )
        )
    return result


def get_all_users():
    return user_model.get_all_users()


def get_user(user_id: str):
    user = user_model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found.")
    return user


def delete_user(user_id: str):
    user = user_model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found.")
    user_model.delete_user(user_id)
    return {"response": "User Deleted Successfully"}


def get_user_history(user_id: str):
    records = borrow_model.get_borrows_by_user(user_id)
    if not records:
        return []

    result = []
    for r in records:
        book = get_book_by_id(r["book_id"])
        result.append(
            GetUserHistoryResp(
                borrow_id=r["id"],
                status=r["status"],
                borrow_date=r["issue_date"],
                due_date=r["due_date"],
                return_date=r.get("returned_date"),
                renewal_count=int(r.get("renewal_count", 0)),
                book=GetBasicBook(
                    id=book["id"] if book else r["book_id"],
                    title=book["title"] if book else "Unknown",
                    author=book["author"] if book else "Unknown",
                    category=book.get("category") if book else None,
                ),
            )
        )
    return result