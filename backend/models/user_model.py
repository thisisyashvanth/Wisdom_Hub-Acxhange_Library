import enum
from core.database import get_table
import uuid
from datetime import datetime, timezone


TABLE = "acxhange-library-users"


class RoleEnum(str, enum.Enum):
    HR = "HR"
    EMPLOYEE = "EMPLOYEE"


def _table():
    return get_table(TABLE)


def create_user(employee_id: str, name: str, email: str, hashed_password: str, role: RoleEnum) -> dict:
    user = {
        "id": str(uuid.uuid4()),
        "employee_id": employee_id,
        "name": name,
        "email": email,
        "hashed_password": hashed_password,
        "role": role.value,
        "is_restricted": False,
        "restricted_until": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _table().put_item(Item=user)
    return user


def get_user_by_id(user_id: str) -> dict | None:
    resp = _table().get_item(Key={"id": user_id})
    return resp.get("Item")


def get_user_by_email(email: str) -> dict | None:
    resp = _table().query(
        IndexName="email-index",
        KeyConditionExpression="email = :e",
        ExpressionAttributeValues={":e": email},
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def get_user_by_employee_id(employee_id: str) -> dict | None:
    resp = _table().query(
        IndexName="employee_id-index",
        KeyConditionExpression="employee_id = :eid",
        ExpressionAttributeValues={":eid": employee_id},
    )
    items = resp.get("Items", [])
    return items[0] if items else None


def get_all_users() -> list:
    resp = _table().scan()
    return resp.get("Items", [])


def update_user(user_id: str, updates: dict) -> dict:
    expr_parts = []
    attr_names = {}
    attr_values = {}

    for key, value in updates.items():
        safe_key = f"#attr_{key}"
        attr_names[safe_key] = key
        attr_values[f":val_{key}"] = value
        expr_parts.append(f"{safe_key} = :val_{key}")

    resp = _table().update_item(
        Key={"id": user_id},
        UpdateExpression="SET " + ", ".join(expr_parts),
        ExpressionAttributeNames=attr_names,
        ExpressionAttributeValues=attr_values,
        ReturnValues="ALL_NEW",
    )
    return resp["Attributes"]


def delete_user(user_id: str):
    _table().delete_item(Key={"id": user_id})