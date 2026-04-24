import enum
from core.database import get_table
from datetime import datetime, timezone
import uuid
from boto3.dynamodb.conditions import Key, Attr


TABLE = "acxhange-library-borrow_records"


class TransactionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    RETURNED = "RETURNED"
    OVERDUE = "OVERDUE"


def _table():
    return get_table(TABLE)


def create_borrow_record(user_id: str, book_id: str, due_date: datetime) -> dict:
    record = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "book_id": book_id,
        "issue_date": datetime.now(timezone.utc).isoformat(),
        "due_date": due_date.isoformat(),
        "returned_date": None,
        "status": TransactionStatus.ACTIVE.value,
        "renewal_count": 0,
    }
    _table().put_item(Item=record)
    return record


def get_borrow_by_id(borrow_id: str) -> dict | None:
    resp = _table().get_item(Key={"id": borrow_id})
    return resp.get("Item")


def get_borrows_by_user(user_id: str) -> list:
    resp = _table().query(
        IndexName="user_id-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
    )
    return resp.get("Items", [])


def get_active_borrow_by_user(user_id: str) -> dict | None:
    resp = _table().query(
        IndexName="user_id-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
        FilterExpression=Attr("status").eq(TransactionStatus.ACTIVE.value),
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def get_borrows_by_book(book_id: str) -> list:
    resp = _table().query(
        IndexName="book_id-index",
        KeyConditionExpression=Key("book_id").eq(book_id),
    )
    return resp.get("Items", [])


def get_borrows_by_status(status: str) -> list:
    resp = _table().query(
        IndexName="status-index",
        KeyConditionExpression=Key("status").eq(status),
    )
    return resp.get("Items", [])


def update_borrow(borrow_id: str, updates: dict) -> dict:
    expr_parts = []
    attr_names = {}
    attr_values = {}

    for key, value in updates.items():
        safe_key = f"#attr_{key}"
        attr_names[safe_key] = key
        attr_values[f":val_{key}"] = value
        expr_parts.append(f"{safe_key} = :val_{key}")

    resp = _table().update_item(
        Key={"id": borrow_id},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp["Attributes"]