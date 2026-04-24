from schemas.auth_schema import UserSignupReq, UserLoginReq 
from models.user_model import get_user_by_email, RoleEnum, create_user, get_user_by_employee_id
from fastapi import HTTPException
from security.security import hash_password, verify_password, create_token 
from schemas.user_schema import GetUserResp


def employee_signup(employee: UserSignupReq):
    if get_user_by_email(employee.email):
        raise HTTPException(status_code=400, detail="User Already Exists.")
    if get_user_by_employee_id(employee.employee_id):
        raise HTTPException(status_code=400, detail="User Already Exists.")

    user = create_user(
        employee_id=employee.employee_id,
        name=employee.name,
        email=employee.email,
        hashed_password=hash_password(employee.password),
        role=RoleEnum.EMPLOYEE,
    )
    return user


def hr_signup(hr: UserSignupReq):
    if get_user_by_email(hr.email):
        raise HTTPException(status_code=400, detail="HR Already Exists.")

    user = create_user(
        employee_id=hr.employee_id,
        name=hr.name,
        email=hr.email,
        hashed_password=hash_password(hr.password),
        role=RoleEnum.HR,
    )
    return user


def login(user: UserLoginReq):
    db_user = get_user_by_email(user.email)

    if not db_user:
        raise HTTPException(status_code=401, detail="User Doesn't Exist. Create an Account First.")

    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid Credentials.")

    payload = {
        "sub": db_user["id"],
        "role": db_user["role"],
    }

    token = create_token(payload)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": GetUserResp.model_validate(db_user),
    }