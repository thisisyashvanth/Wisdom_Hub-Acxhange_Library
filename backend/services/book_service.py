from schemas.book_schema import CreateBookReq, UpdateBookReq
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

# Pagination Version
# def get_all_books(limit: int = 10, last_key: dict | None = None):
#     return book_model.get_all_books(limit, last_key)


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


def update_book(book_id: str, book: UpdateBookReq) -> dict:
    existing = book_model.get_book_by_id(book_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Book Not Found.")

    # Uniqueness: ISBN must not belong to a different book
    # isbn_match = book_model.get_book_by_isbn(book.isbn)
    # if isbn_match and isbn_match["id"] != book_id:
    #     raise HTTPException(status_code=400, detail="Book with this ISBN already exists.")

    num_match = book_model.get_book_by_number(book.bookNumber)
    if num_match and num_match["id"] != book_id:
        raise HTTPException(status_code=400, detail="Book with this Book Number already exists.")

    borrowed_copies = int(existing["total_copies"]) - int(existing["available_copies"])
    new_available = book.total_copies - borrowed_copies

    if new_available < 0:
        raise HTTPException(
            status_code=400,
            detail="Total copies cannot be less than the number of currently borrowed copies."
        )

    updates = {
        "title": book.title,
        "author": book.author,
        "bookNumber": book.bookNumber,
        "isbn": book.isbn,
        "category": book.category,
        "total_copies": book.total_copies,
        "available_copies": new_available,
    }
    return book_model.update_book(book_id, updates)


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