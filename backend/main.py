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
    now = datetime.now(timezone.utc)
    tomorrow_date = (now + timedelta(days=1)).date()

    active_borrows = borrow_model.get_borrows_by_status(
        TransactionStatus.ACTIVE.value
    )

    print("Total active borrows:", len(active_borrows))

    for borrow in active_borrows:
        try:
            due_dt = datetime.fromisoformat(borrow["due_date"])
            due_date = due_dt.date()

            if due_date != tomorrow_date:
                continue

            user = user_model.get_user_by_id(borrow["user_id"])
            if not user:
                print("User not found:", borrow["user_id"])
                continue

            book = book_model.get_book_by_id(borrow["book_id"])
            book_title = book["title"] if book else "Unknown"

            issue_dt = datetime.fromisoformat(borrow["issue_date"])
            formatted_issue_date = issue_dt.strftime("%d %b %Y")
            formatted_due_date = due_dt.strftime("%d %b %Y")

            renewal_count = int(borrow.get("renewal_count", 0))

            if renewal_count >= 1:
                message = f"""
Dear {user['name']},

This is a reminder regarding the library book you had taken on {formatted_issue_date} and subsequently renewed once.

Kindly ensure that the book "{book_title}" is returned tomorrow ({formatted_due_date}) in the second half to avoid any further action as per policy.

The timings will be communicated shortly. Kindly ensure the book is brought accordingly.

Thank you for your cooperation.

Best regards,  
WisdomHub Library  
Acxhange
"""

            else:
                message = f"""
Dear {user['name']},

This is to inform you that the book "{book_title}" issued on {formatted_issue_date} must be either returned or renewed tomorrow ({formatted_due_date}) during the second half of the day.

The timings will be communicated shortly. Kindly ensure the book is brought accordingly for return or renewal.

Thank you for your cooperation.

Best regards,  
WisdomHub Library  
Acxhange
"""

            print(f"Sending email to {user['email']} | Renewal count: {renewal_count}")

            sns.publish(
                TopicArn=TOPIC_ARN,
                Subject="WisdomHub Reminder: Library Item Due Tomorrow",
                Message=message
            )

        except Exception as e:
            print(f"Error processing borrow {borrow.get('id')}: {str(e)}")

def reminder_handler(event, context):
    print("Reminder handler triggered")
    send_due_reminders()
    return {"status": "done"}


handler = Mangum(app)