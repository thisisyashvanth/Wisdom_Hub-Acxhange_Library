from fastapi import APIRouter, Depends, HTTPException, Query
from security.dependency import get_current_user, require_hr
from services.request_service import (
    lift_expired_restrictions, create_borrow_request, create_renew_request,
    create_return_request, review_request, check_and_flag_overdue, 
    get_all_requests, get_my_requests,
)
from schemas.request_schema import ReviewRequestBody
from typing import List
from models.request_model import RequestStatus, RequestType
from services import request_service


router = APIRouter(prefix="/request", tags=["Requests"])


@router.post("/borrow/{book_id}")
def request_borrow(book_id: str, user=Depends(get_current_user)):
    lift_expired_restrictions()
    try:
        return create_borrow_request(book_id, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/renew/{borrow_id}")
def request_renew(borrow_id: str, user=Depends(get_current_user)):
    try:
        return create_renew_request(borrow_id, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/return/{borrow_id}")
def request_return(borrow_id: str, user=Depends(get_current_user)):
    try:
        return create_return_request(borrow_id, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{request_id}/review")
def review_request_endpoint(request_id: str, body: ReviewRequestBody, user=Depends(require_hr)):
    try:
        return review_request(request_id, body.approve, body.remarks, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/admin/check-overdue")
def check_overdue(hr=Depends(require_hr)):
    try:
        return check_and_flag_overdue()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/admin/lift-restrictions")
def lift_restrictions(hr=Depends(require_hr)):
    try:
        return lift_expired_restrictions()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/requests")
def get_all_requests_endpoint(
    status: List[RequestStatus] | None = Query(default=None),
    request_type: RequestType | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    hr=Depends(require_hr),
):
    
    statuses = [s.value for s in status] if status else None
    requests = request_service.get_all_requests(statuses, request_type, search)

    total = len(requests)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = requests[start:end]

    return {
        "data": [
            {
                "request_id": r["id"],
                "employee_id": r["employee_id"],
                "employee_name": r["employee_name"],
                "book_id": r["book_id"],
                "book_name": r["book_name"],
                "request_type": r["request_type"],
                "status": r["status"],
                "requested_at": r["requested_at"],
                "reviewed_at": r.get("reviewed_at"),
                "remarks": r.get("remarks"),
            }
            for r in paginated
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/my-requests")
def get_my_requests_endpoint(user=Depends(get_current_user)):
    requests = get_my_requests(user)
    return [
        {
            "request_id": r["id"],
            "book_name": r.get("book_name", ""),
            "request_type": r["request_type"],
            "status": r["status"],
            "requested_at": r["requested_at"],
            "reviewed_at": r.get("reviewed_at"),
            "remarks": r.get("remarks"),
        }
        for r in requests
    ]