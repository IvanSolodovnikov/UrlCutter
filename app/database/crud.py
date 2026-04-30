from .db import new_session
from .models import ShortUrl, Admin
from sqlalchemy import select, delete, and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

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

async def get_all_slugs() -> list[ShortUrl]:
    async with new_session() as session:
        query = select(ShortUrl)
        result = await session.execute(query)
        return list(result.scalars().all())

async def get_all_slugs_by_user_id(user_id: str) -> list[ShortUrl]:
    async with new_session() as session:
        query = select(ShortUrl).filter_by(user_id=user_id)
        result = await session.execute(query)
        return list(result.scalars().all())

async def get_admin_by_login(login: str):
    async with new_session() as session:
        try:
            query = select(Admin).where(
                Admin.login == login
            )

            result = await session.execute(query)
            admin = result.scalar_one_or_none()
        except SQLAlchemyError:
            return None

        return admin

async def get_slug_from_db(slug:str) -> ShortUrl | None:
    async with new_session() as session:
        try:
            query = select(ShortUrl).where(ShortUrl.slug == slug)

            result = await session.execute(query)
        except SQLAlchemyError:
            return None

        return  result.scalar_one_or_none()

async def get_slugs_by_url_from_db(url: str) -> list[ShortUrl] | None:
    async with new_session() as session:
        try:
            query = select(ShortUrl).where(ShortUrl.long_url == url)

            result = await session.execute(query)
        except SQLAlchemyError:
            return None

        return list(result.scalars().all())

async def get_slugs_by_user_id_from_db(user_id: str) -> list[ShortUrl] | None:
    async with new_session() as session:
        try:
            query = select(ShortUrl).where(ShortUrl.user_id == user_id)

            result = await session.execute(query)
        except SQLAlchemyError:
            return None

        return list(result.scalars().all())

async def get_slugs_by_filters_from_db(slug: str,
                                       url: str,
                                       user_id: str) -> list[ShortUrl] | None:
    async with new_session() as session:
        try:
            conditions = []

            if slug is not None:
                conditions.append(ShortUrl.slug == slug)
            if url is not None:
                conditions.append(ShortUrl.long_url == url)
            if user_id is not None:
                conditions.append(ShortUrl.user_id == user_id)
            if conditions:
                query = select(ShortUrl).where(and_(*conditions))

            result = await session.execute(query)
        except SQLAlchemyError:
            return None

        return list(result.scalars().all())