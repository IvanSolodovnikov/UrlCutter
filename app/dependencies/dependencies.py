import uuid

from fastapi import Request, Response, HTTPException, status

from app.auth.jwt import decode_admin_token
from app.database.crud import get_admin_by_login


def get_or_create_user_id(request: Request, response: Response) -> str:
    user_id = request.cookies.get('user_id')

    if not user_id:
        user_id = str(uuid.uuid4())

    response.set_cookie(key="user_id",
        value=user_id,
        httponly=True,
        max_age=60 * 60 * 24 * 365 * 7)

    return user_id


async def get_current_admin(request: Request) -> str:
    auth_header = request.headers.get("authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация"
        )

    token = auth_header.split(" ")[1]
    payload = decode_admin_token(token)

    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )

    correct_admin_login = await get_admin_by_login(payload["sub"])

    if not correct_admin_login:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )

    return payload["sub"]
