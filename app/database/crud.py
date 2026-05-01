from .db import new_session
from .models import ShortUrl, Admin
from sqlalchemy import select, delete, and_, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from ..exeptions import SlugAlreadyExistsError, SlugDoesntExistError, DatabaseError, SlugNotAvailableError, \
    NoLongUrlFoundError


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
        if not res:
            raise NoLongUrlFoundError()
        if not res.available:
            raise SlugNotAvailableError()
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

async def get_slugs_by_filters_from_db(slug: str | None = None,
                                       url: str | None = None,
                                       user_id: str | None = None) -> list[ShortUrl]:
    async with new_session() as session:
        try:
            conditions = []

            if slug is not None:
                conditions.append(ShortUrl.slug == slug)
            if url is not None:
                conditions.append(ShortUrl.long_url == url)
            if user_id is not None:
                conditions.append(ShortUrl.user_id == user_id)

            query = select(ShortUrl)
            if conditions:
                query = query.where(and_(*conditions))

            result = await session.execute(query)
        except SQLAlchemyError:
            return None

        return list(result.scalars().all())

async def delete_slug_by_admin_from_db(slug: str):
    async with new_session() as session:
        query = delete(ShortUrl).where(
            ShortUrl.slug == slug,
        )
        await session.execute(query)

        try:
            await session.commit()
        except Exception:
            raise SlugDoesntExistError

async def slug_block_in_db(slug: str):
    async with new_session() as session:
        query_select = select(ShortUrl.available).where(ShortUrl.slug == slug)
        result = await session.execute(query_select)
        current_available = result.scalar_one_or_none()

        if current_available is None:
            raise SlugDoesntExistError(f"Slug '{slug}' не существует")

        new_available = not current_available

        query = update(ShortUrl).where(
            ShortUrl.slug == slug
        ).values(available=new_available)

        await session.execute(query)

        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise DatabaseError(f"Не удалось переключить статус slug '{slug}'")