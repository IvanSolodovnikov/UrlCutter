from .db import new_session
from .models import ShortUrl
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from ..exeptions import SlugAlreadyExistsError, SlugDoesntExistError


async def add_slug_to_db(
        slug: str,
        url: str,
        user_id: str
):
    async with new_session() as session:
        new_slug = ShortUrl(
            slug=slug,
            long_url=url,
            user_id = user_id
        )
        session.add(new_slug)
        try:
            await session.commit()
        except IntegrityError:
            raise SlugAlreadyExistsError


async def get_long_url_by_slug_from_db(slug: str) -> str|None:
    async with new_session() as session:
        query = select(ShortUrl).filter_by(slug=slug)
        result = await session.execute(query)
        res: ShortUrl | None = result.scalar_one_or_none()
        return res.long_url if res else None

async def delete_slug_by_user_id(slug: str, user_id: str):
    async with new_session() as session:
        query = delete(ShortUrl).where(
            ShortUrl.slug == slug,
            ShortUrl.user_id == user_id
        )
        await session.execute(query)

        try:
            await session.commit()
        except Exception:
            raise SlugDoesntExistError


async def get_all_slugs_by_user_id(user_id: str) -> list[ShortUrl]:
    async with new_session() as session:
        query = select(ShortUrl).filter_by(user_id=user_id)
        result = await session.execute(query)
        return list(result.scalars().all())

