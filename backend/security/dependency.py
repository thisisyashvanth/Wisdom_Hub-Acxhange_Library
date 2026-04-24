from fastapi.security import OAuth2PasswordBearer
import os
from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from models.user_model import get_user_by_id, RoleEnum 


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")

        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid Token.")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token.")

    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=401, detail="User Not Found.")

    if user["role"] != role:
        raise HTTPException(status_code=403, detail="Token Role Mismatch.")

    if user.get("is_restricted"):
        raise HTTPException(status_code=403, detail="User is Restricted.")

    return user


def require_hr(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != RoleEnum.HR.value:
        raise HTTPException(status_code=403, detail="HR Access Required.")
    return current_user