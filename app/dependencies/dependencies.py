import uuid

from fastapi import Request, Response


def get_or_create_user_id(request: Request, response: Response) -> str:
    user_id = request.cookies.get('user_id')

    if not user_id:
        user_id = str(uuid.uuid4())

        response.set_cookie(key="user_id",
                            value=user_id,
                            httponly=True,
                            max_age=60 * 60 * 24 * 365 * 7)

    return user_id