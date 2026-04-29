from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.user_api import router as user_router
from api.auth_api import router as auth_router
from api.book_api import router as book_router
from api.request_api import router as request_router
from api.excel_api import router as excel_router
from mangum import Mangum

import boto3
from datetime import datetime, timedelta, timezone
from models import book_model
from models import borrow_model, user_model
from models.borrow_model import TransactionStatus


app = FastAPI(title="Wisdom Hub - Acxhange Library")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Add CDN Deployed Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(book_router)
app.include_router(request_router)
app.include_router(excel_router)


@app.get("/setup")
def setup():
    return {"message": "Run: core/dynamo_tables.py, success."}


sns = boto3.client('sns', region_name='ap-south-1')

TOPIC_ARN = "arn:aws:sns:ap-south-1:320644769527:acxhange-library-reminders"

def send_due_reminders():
    tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
    tomorrow_date = tomorrow.date()

    active_borrows = borrow_model.get_borrows_by_status(
        TransactionStatus.ACTIVE.value
    )

    for borrow in active_borrows:
        due_date = datetime.fromisoformat(borrow["due_date"]).date()

        # Testing
        if True:

        # Actual
        # if due_date == tomorrow_date:

            user = user_model.get_user_by_id(borrow["user_id"])
            if not user:
                continue

            book = book_model.get_book_by_id(borrow["book_id"])
            book_title = book["title"] if book else "Unknown"

            message = f"""
Reminder: Book due tomorrow

User: {user['name']}
Book: {book_title}
Due Date: {borrow['due_date']}

Please return or renew it.
"""

            try:
                sns.publish(
                    TopicArn=TOPIC_ARN,
                    Subject="WisdomHub - Book Reminder",
                    Message=message
                )
            except Exception as e:
                print(f"Failed to publish message: {str(e)}")





def reminder_handler(event, context):
    print("Reminder handler triggered")
    send_due_reminders()
    return {"status": "done"}


handler = Mangum(app)