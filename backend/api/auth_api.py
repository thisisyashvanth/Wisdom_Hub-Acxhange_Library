from fastapi import APIRouter
from schemas.auth_schema import UserSignupResp, UserSignupReq, UserLoginResp, UserLoginReq 
from services import auth_service


router = APIRouter(prefix="/auth", tags=["Auth Routes"])


@router.post("/signup", response_model=UserSignupResp)
def employee_signup(employee: UserSignupReq):
    return auth_service.employee_signup(employee)


@router.post("/hr-signup", response_model=UserSignupResp)
def hr_signup(hr: UserSignupReq):
    return auth_service.hr_signup(hr)


@router.post("/login", response_model=UserLoginResp)
def login(user: UserLoginReq):
    return auth_service.login(user)