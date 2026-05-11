from datetime import datetime, timedelta, timezone
from models import borrow_model, request_model, book_model, user_model
from models.request_model import RequestType, RequestStatus 
from models.borrow_model import TransactionStatus


MAX_RENEWALS = 1
RESTRICTION_DAYS = 30

from models.book_model import get_book_by_id

def attach_book_name(requests: list) -> list:
    for r in requests:
        book = get_book_by_id(r["book_id"])
        if book:
            r["book_name"] = book.get("title", "Unknown Book")
        else:
            r["book_name"] = "Unknown Book"
    return requests


def _get_fourth_tuesday(from_date: datetime) -> datetime:
    d = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
    # Find the most recent Tuesday on or before from_date (look backwards, not forwards).
    # This ensures that if the issue day is postponed (e.g. to Wednesday), we still
    # anchor to that same week's Tuesday rather than the next week's Tuesday.
    days_since_tuesday = (d.weekday() - 1) % 7  # 0 if today is Tue, 1 if Wed, 6 if Mon
    this_weeks_tuesday = d - timedelta(days=days_since_tuesday)
    return this_weeks_tuesday + timedelta(weeks=4)

    
# Toggle For Testing
def _is_tuesday_second_half() -> bool:
    return True


def create_borrow_request(book_id: str, user: dict):
    if not _is_tuesday_second_half():
        raise Exception("Borrow Requests can only be made on Tuesdays between 12:00 PM and 6:00 PM.")

    if user.get("is_restricted"):
        raise Exception("You are Restricted from Borrowing Books.")

    if borrow_model.get_active_borrow_by_user(user["id"]):
        raise Exception("You already have an Active Borrowed Book.")

    if request_model.get_pending_borrow_request(user["id"], book_id):
        raise Exception("Borrow Request already Pending for this Book.")

    if not book_model.get_book_by_id(book_id):
        raise Exception("Book Not Found.")

    req = request_model.create_request(user["id"], book_id, RequestType.BORROW)
    return {"message": "Borrow request created", "request_id": req["id"]}


def create_renew_request(borrow_id: str, user: dict):
    if not _is_tuesday_second_half():
        raise Exception("Renewals can only be Requested on Tuesdays after 12:00 PM.")

    borrow = borrow_model.get_borrow_by_id(borrow_id)
    if not borrow or borrow["user_id"] != user["id"]:
        raise Exception("Borrow Record not Found.")

    if borrow["status"] != TransactionStatus.ACTIVE.value:
        raise Exception("Cannot Renew this Book.")

    if int(borrow.get("renewal_count", 0)) >= MAX_RENEWALS:
        raise Exception("Renewal Limit Reached. Please Return the Book.")

    if request_model.get_pending_request_for_borrow(user["id"], borrow_id):
        raise Exception("Request Already Pending.")

    req = request_model.create_request(user["id"], borrow["book_id"], RequestType.RENEW, borrow_id)
    return {"message": "Renew request created", "request_id": req["id"]}


def create_return_request(borrow_id: str, user: dict):
    if not _is_tuesday_second_half():
        raise Exception("Returns can only be Requested on Tuesdays after 12:00 PM.")

    borrow = borrow_model.get_borrow_by_id(borrow_id)
    if not borrow or borrow["user_id"] != user["id"]:
        raise Exception("Borrow Record not Found.")

    if borrow["status"] != TransactionStatus.ACTIVE.value:
        raise Exception("Already Returned")

    if request_model.get_pending_request_for_borrow(user["id"], borrow_id):
        raise Exception("Request Already Pending.")

    req = request_model.create_request(user["id"], borrow["book_id"], RequestType.RETURN, borrow_id)
    return {"message": "Return Request Created", "request_id": req["id"]}


def review_request(request_id: str, approve: bool, remarks: str | None, hr_user: dict):
    if not _is_tuesday_second_half():
        raise Exception("Requests can only be Reviewed on Tuesdays between 12:00 PM and 6:00 PM.")

    req = request_model.get_request_by_id(request_id)
    if not req:
        raise Exception("Request Not Found.")

    if req["status"] != RequestStatus.PENDING.value:
        raise Exception("Already Reviewed.")

    now = datetime.now(timezone.utc)

    if not approve:
        if not remarks:
            raise Exception("Remarks are Required for Rejection.")
        request_model.update_request(request_id, {
            "status": RequestStatus.REJECTED.value,
            "remarks": remarks,
            "reviewed_by": hr_user["id"],
            "reviewed_at": now.isoformat(),
        })
        return {"message": "Request Rejected"}

    req_type = req["request_type"]

    if req_type == RequestType.BORROW.value:
        _approve_borrow(req, hr_user, now)
    elif req_type == RequestType.RENEW.value:
        _approve_renew(req)
    elif req_type == RequestType.RETURN.value:
        _approve_return(req)

    updates = {
        "status": RequestStatus.APPROVED.value,
        "reviewed_by": hr_user["id"],
        "reviewed_at": now.isoformat(),
    }
    if remarks:
        updates["remarks"] = remarks

    request_model.update_request(request_id, updates)
    return {"message": "Request Approved"}


def _approve_borrow(req: dict, hr_user: dict, now: datetime):
    book = book_model.get_book_by_id(req["book_id"])
    if not book:
        raise Exception("Book Not Found.")

    if int(book["available_copies"]) <= 0:
        request_model.update_request(req["id"], {
            "status": RequestStatus.REJECTED.value,
            "reviewed_by": hr_user["id"],
            "reviewed_at": now.isoformat(),
            "remarks": "Auto-Rejected: No Copies Available.",
        })
        raise Exception("No Copies Available. Request Auto-Rejected.")

    due_date = _get_fourth_tuesday(now)

    borrow_model.create_borrow_record(
        user_id=req["user_id"],
        book_id=req["book_id"],
        due_date=due_date,
    )

    book_model.update_book(req["book_id"], {
        "available_copies": int(book["available_copies"]) - 1
    })

    # Auto-reject other pending borrow requests for this user
    other_pending = request_model.get_pending_borrow_requests_by_user(req["user_id"], req["id"])
    for other in other_pending:
        request_model.update_request(other["id"], {
            "status": RequestStatus.REJECTED.value,
            "reviewed_by": hr_user["id"],
            "reviewed_at": now.isoformat(),
            "remarks": "Auto-Rejected: Another Borrow Request was Approved.",
        })


def _approve_renew(req: dict):
    borrow = borrow_model.get_borrow_by_id(req["borrow_id"])
    if not borrow:
        raise Exception("Borrow record not found")

    if int(borrow.get("renewal_count", 0)) >= MAX_RENEWALS:
        raise Exception("Renewal limit reached")

    current_due = datetime.fromisoformat(borrow["due_date"])
    new_due = _get_fourth_tuesday(current_due)

    borrow_model.update_borrow(borrow["id"], {
        "due_date": new_due.isoformat(),
        "renewal_count": int(borrow.get("renewal_count", 0)) + 1,
    })


# def _approve_return(req: dict):
#     borrow = borrow_model.get_borrow_by_id(req["borrow_id"])
#     if not borrow:
#         raise Exception("Borrow record not found")

#     borrow_model.update_borrow(borrow["id"], {
#         "status": TransactionStatus.RETURNED.value,
#         "returned_date": datetime.now(timezone.utc).isoformat(),
#     })

#     book = book_model.get_book_by_id(borrow["book_id"])
#     if book:
#         book_model.update_book(book["id"], {
#             "available_copies": int(book["available_copies"]) + 1
#         })


def _return_borrow_core(borrow: dict):
    borrow_model.update_borrow(borrow["id"], {
        "status": TransactionStatus.RETURNED.value,
        "returned_date": datetime.now(timezone.utc).isoformat(),
    })

    book = book_model.get_book_by_id(borrow["book_id"])
    if book:
        book_model.update_book(book["id"], {
            "available_copies": int(book["available_copies"]) + 1
        })


def _approve_return(req: dict):
    borrow = borrow_model.get_borrow_by_id(req["borrow_id"])
    if not borrow:
        raise Exception("Borrow record not found")

    _return_borrow_core(borrow)


def check_and_flag_overdue():
    now = datetime.now(timezone.utc)
    active_records = borrow_model.get_borrows_by_status(TransactionStatus.ACTIVE.value)

    overdue_count = 0

    for record in active_records:
        due_date = datetime.fromisoformat(record["due_date"])

        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        if due_date < now:
            overdue_count += 1

            borrow_model.update_borrow(record["id"], {
                "status": TransactionStatus.OVERDUE.value
            })

    return {"overdue_count": overdue_count}


# def check_and_flag_overdue():
#     now = datetime.now(timezone.utc)
#     active_records = borrow_model.get_borrows_by_status(TransactionStatus.ACTIVE.value)
#     restricted_users = []

#     for record in active_records:
#         due_date = datetime.fromisoformat(record["due_date"])
#         if due_date.tzinfo is None:
#             due_date = due_date.replace(tzinfo=timezone.utc)

#         if due_date < now:
#             borrow_model.update_borrow(record["id"], {
#                 "status": TransactionStatus.OVERDUE.value
#             })

#         # if due_date < now:
#         #     borrow_model.update_borrow(record["id"], {"status": TransactionStatus.OVERDUE.value})

#         #     user = user_model.get_user_by_id(record["user_id"])
#         #     if user and not user.get("is_restricted"):
#         #         restricted_until = now + timedelta(days=RESTRICTION_DAYS)
#         #         user_model.update_user(record["user_id"], {
#         #             "is_restricted": True,
#         #             "restricted_until": restricted_until.isoformat(),
#         #         })
#         #         restricted_users.append(user["name"])

#     return {"overdue_count": len(active_records), "restricted_users": restricted_users}


# def lift_expired_restrictions():
#     now = datetime.now(timezone.utc)
#     all_users = user_model.get_all_users()
#     lifted = 0

#     for user in all_users:
#         if not user.get("is_restricted"):
#             continue
#         restricted_until = user.get("restricted_until")
#         if not restricted_until:
#             continue
#         ru = datetime.fromisoformat(restricted_until)
#         if ru.tzinfo is None:
#             ru = ru.replace(tzinfo=timezone.utc)
#         if ru <= now:
#             user_model.update_user(user["id"], {
#                 "is_restricted": False,
#                 "restricted_until": None,
#             })
#             lifted += 1

#     return {"lifted_count": lifted}


def get_all_requests(statuses=None, request_type=None, search=None):
    requests = request_model.get_all_requests(
        status=None,
        request_type=request_type.value if request_type else None,
    )

    enriched = []

    for r in requests:
        user = user_model.get_user_by_id(r["user_id"])
        book = book_model.get_book_by_id(r["book_id"])

        enriched.append({
            **r,
            "employee_id": user.get("employee_id") if user else "",
            "employee_name": user.get("name") if user else "",
            "book_name": book.get("title") if book else "",
        })

    if statuses:
        enriched = [r for r in enriched if r["status"] in statuses]

    if search:
        search_lower = search.lower()

        enriched = [
            r for r in enriched
            if search_lower in (r.get("book_name") or "").lower()
            or search_lower in (r.get("employee_name") or "").lower()
            or search_lower in (r.get("status") or "").lower()
            or search_lower in (r.get("request_type") or "").lower()
        ]

    return enriched


def get_my_requests(user: dict):
    # return request_model.get_my_requests(user["id"])
    items = request_model.get_my_requests(user["id"])
    items = attach_book_name(items)   
    return items