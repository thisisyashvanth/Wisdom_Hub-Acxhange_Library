from fastapi import APIRouter, Depends
from schemas.user_schema import GetUserBooksResp, GetUserResp, DeleteUserResp, GetUserHistoryResp
from security.dependency import get_current_user, require_hr
from services import user_service


router = APIRouter(prefix="/users", tags=["User Routes"])


@router.get("/books", response_model=list[GetUserBooksResp])
def get_my_books(current_user=Depends(get_current_user)):
    return user_service.get_my_books(current_user)


@router.get("/get-all", response_model=list[GetUserResp])
def get_all_users(hr=Depends(require_hr)):
    return user_service.get_all_users()


@router.get("/{id}", response_model=GetUserResp)
def get_user(id: str):
    return user_service.get_user(id)


@router.delete("/{id}", response_model=DeleteUserResp)
def delete_user(id: str, hr=Depends(require_hr)):
    return user_service.delete_user(id)


@router.get("/{id}/history", response_model=list[GetUserHistoryResp])
def get_user_history(id: str, current_user=Depends(get_current_user)):
    return user_service.get_user_history(id)