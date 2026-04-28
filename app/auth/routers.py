from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.auth.jwt import create_admin_token
from app.auth.security import verify_password
from app.database.crud import get_admin_by_login


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


class AdminLoginRequest(BaseModel):
    login: str
    password: str


@router.post("/login")
async def admin_login(data: AdminLoginRequest):
    admin = await get_admin_by_login(data.login)

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )

    if not verify_password(data.password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )

    access_token = create_admin_token(
        {"sub": admin.login}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }