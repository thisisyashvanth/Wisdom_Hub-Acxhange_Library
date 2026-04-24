import os
import boto3


try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT", None)


def get_dynamodb():
    kwargs = {"region_name": AWS_REGION}
    if DYNAMODB_ENDPOINT:
        kwargs["endpoint_url"] = DYNAMODB_ENDPOINT
    return boto3.resource("dynamodb", **kwargs)


def get_table(table_name: str):
    return get_dynamodb().Table(table_name)