import enum
from core.database import get_table
import uuid
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key, Attr


TABLE = "acxhange-library-requests"


class RequestType(str, enum.Enum):
    BORROW = "BORROW"
    RETURN = "RETURN"
    RENEW = "RENEW"


class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


def _table():
    return get_table(TABLE)


def create_request(user_id: str, book_id: str, request_type: RequestType, borrow_id: str | None = None) -> dict:
    req = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "book_id": book_id,
        "borrow_id": borrow_id,
        "request_type": request_type.value,
        "status": RequestStatus.PENDING.value,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "reviewed_at": None,
        "reviewed_by": None,
        "remarks": None,
    }
    _table().put_item(Item=req)
    return req


def get_request_by_id(request_id: str) -> dict | None:
    resp = _table().get_item(Key={"id": request_id})
    return resp.get("Item")


def get_requests_by_user(user_id: str) -> list:
    resp = _table().query(
        IndexName="user_id-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
    )
    return resp.get("Items", [])


def get_pending_borrow_request(user_id: str, book_id: str) -> dict | None:
    resp = _table().query(
        IndexName="user_id-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
        FilterExpression=Attr("book_id").eq(book_id)
            & Attr("request_type").eq(RequestType.BORROW.value)
            & Attr("status").eq(RequestStatus.PENDING.value),
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def get_pending_request_for_borrow(user_id: str, borrow_id: str) -> dict | None:
    resp = _table().query(
        IndexName="user_id-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
        FilterExpression=Attr("borrow_id").eq(borrow_id)
            & Attr("status").eq(RequestStatus.PENDING.value),
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def get_all_requests(status: str | None = None, request_type: str | None = None) -> list:
    if status:
        resp = _table().query(
            IndexName="status-index",
            KeyConditionExpression=Key("status").eq(status),
        )
        items = resp.get("Items", [])
        if request_type:
            items = [r for r in items if r["request_type"] == request_type]
    else:
        resp = _table().scan()
        items = resp.get("Items", [])
        if request_type:
            items = [r for r in items if r["request_type"] == request_type]

    return sorted(items, key=lambda x: x.get("requested_at", ""), reverse=True)


def get_my_requests(user_id: str) -> list:
    resp = _table().query(
        IndexName="user_id-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
        FilterExpression=Attr("status").ne(RequestStatus.PENDING.value),
    )
    items = resp.get("Items", [])
    return sorted(items, key=lambda x: x.get("requested_at", ""), reverse=True)


def update_request(request_id: str, updates: dict) -> dict:
    expr_parts = []
    attr_names = {}
    attr_values = {}

    for key, value in updates.items():
        safe_key = f"#attr_{key}"
        attr_names[safe_key] = key
        attr_values[f":val_{key}"] = value
        expr_parts.append(f"{safe_key} = :val_{key}")

    resp = _table().update_item(
        Key={"id": request_id},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp["Attributes"]


def get_pending_borrow_requests_by_user(user_id: str, exclude_request_id: str) -> list:
    resp = _table().query(
        IndexName="user_id-index",
        KeyConditionExpression=Key("user_id").eq(user_id),
        FilterExpression=Attr("request_type").eq(RequestType.BORROW.value)
            & Attr("status").eq(RequestStatus.PENDING.value),
    )
    return [r for r in resp.get("Items", []) if r["id"] != exclude_request_id]