from core.database import get_table
import uuid


TABLE = "acxhange-library-bookss"


def _table():
    return get_table(TABLE)


def create_book(title: str, bookNumber: str, author: str, isbn: str, category: str, total_copies: int) -> dict:
    book = {
        "id": str(uuid.uuid4()),
        "title": title,
        "bookNumber": bookNumber,
        "author": author,
        "isbn": isbn,
        "category": category,
        "total_copies": total_copies,
        "available_copies": total_copies,
    }
    _table().put_item(Item=book)
    return book


def get_book_by_id(book_id: str) -> dict | None:
    resp = _table().get_item(Key={"id": book_id})
    return resp.get("Item")


def get_book_by_isbn(isbn: str) -> dict | None:
    resp = _table().query(
        IndexName="isbn-index",
        KeyConditionExpression="isbn = :i",
        ExpressionAttributeValues={":i": isbn},
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def get_book_by_number(book_number: str) -> dict | None:
    resp = _table().query(
        IndexName="bookNumber-index",
        KeyConditionExpression="bookNumber = :bn",
        ExpressionAttributeValues={":bn": book_number},
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def get_all_books() -> list:
    resp = _table().scan()
    return resp.get("Items", [])

# Pagination Version
# def get_all_books(limit: int = 10, last_key: dict | None = None):
#     params = {
#         "Limit": limit
#     }

#     if last_key:
#         params["ExclusiveStartKey"] = last_key

#     resp = _table().scan(**params)

#     return {
#         "items": resp.get("Items", []),
#         "last_key": resp.get("LastEvaluatedKey")
#     }


def update_book(book_id: str, updates: dict) -> dict:
    expr_parts = []
    attr_names = {}
    attr_values = {}

    for key, value in updates.items():
        safe_key = f"#attr_{key}"
        attr_names[safe_key] = key
        attr_values[f":val_{key}"] = value
        expr_parts.append(f"{safe_key} = :val_{key}")

    resp = _table().update_item(
        Key={"id": book_id},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp["Attributes"]


def delete_book(book_id: str):
    _table().delete_item(Key={"id": book_id})