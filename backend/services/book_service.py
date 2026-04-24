from schemas.book_schema import CreateBookReq
from models import book_model, borrow_model, user_model
from fastapi import HTTPException


def create_book(book: CreateBookReq):
    if book_model.get_book_by_isbn(book.isbn):
        raise HTTPException(status_code=400, detail="Book with this ISBN already Exists.")
    if book_model.get_book_by_number(book.bookNumber):
        raise HTTPException(status_code=400, detail="Book with this Book Number already Exists.")

    return book_model.create_book(
        title=book.title,
        bookNumber=book.bookNumber,
        author=book.author,
        isbn=book.isbn,
        category=book.category,
        total_copies=book.total_copies,
    )


def get_all_books():
    return book_model.get_all_books()


def get_book(book_id: str):
    book = book_model.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book Not Found.")
    return book


def delete_book(book_id: str):
    book = book_model.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book Not Found.")

    if int(book["available_copies"]) != int(book["total_copies"]):
        raise HTTPException(status_code=400, detail="Cannot Delete Book. Some Copies are Currently Issued to Employees.")

    book_model.delete_book(book_id)
    return {"title": book["title"], "response": "Book Deleted Successfully."}


def get_book_user_history(book_id: str):
    book = book_model.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book Not Found.")

    records = borrow_model.get_borrows_by_book(book_id)
    result = []

    for r in records:
        user = user_model.get_user_by_id(r["user_id"])
        result.append({
            "borrow_id": r["id"],
            "user_id": r["user_id"],
            "employee_id": user["employee_id"] if user else "Unknown",
            "employee_name": user["name"] if user else "Unknown",
            "issue_date": r["issue_date"],
            "due_date": r["due_date"],
            "returned_date": r.get("returned_date"),
            "status": r["status"],
            "renewal_count": int(r.get("renewal_count", 0)),
        })

    return result