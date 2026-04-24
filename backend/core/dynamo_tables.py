import os
import boto3


try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", None)


def get_client():
    kwargs = {"region_name": AWS_REGION}
    if DYNAMODB_ENDPOINT:
        kwargs["endpoint_url"] = DYNAMODB_ENDPOINT
    return boto3.client("dynamodb", **kwargs)


TABLES = [
    {
        "TableName": "acxhange-library-users",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "email", "AttributeType": "S"},
            {"AttributeName": "employee_id", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "email-index",
                "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "employee_id-index",
                "KeySchema": [{"AttributeName": "employee_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "acxhange-library-books",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "isbn", "AttributeType": "S"},
            {"AttributeName": "bookNumber", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "isbn-index",
                "KeySchema": [{"AttributeName": "isbn", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "bookNumber-index",
                "KeySchema": [{"AttributeName": "bookNumber", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "acxhange-library-borrow_records",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "book_id", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "user_id-index",
                "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "book_id-index",
                "KeySchema": [{"AttributeName": "book_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "status-index",
                "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "acxhange-library-requests",
        "KeySchema": [{"AttributeName": "id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "id", "AttributeType": "S"},
            {"AttributeName": "user_id", "AttributeType": "S"},
            {"AttributeName": "status", "AttributeType": "S"},
        ],
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "user_id-index",
                "KeySchema": [{"AttributeName": "user_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "status-index",
                "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        "BillingMode": "PAY_PER_REQUEST",
    },
]


def create_tables():
    client = get_client()
    existing = client.list_tables()["TableNames"]

    for table_def in TABLES:
        name = table_def["TableName"]
        if name in existing:
            print(f"[SKIP] {name} already exists")
            continue
        client.create_table(**table_def)
        print(f"[CREATED] {name}")

    print("Done.")


if __name__ == "__main__":
    create_tables()