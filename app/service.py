from .database.crud import (add_slug_to_db, get_long_url_by_slug_from_db, delete_slug_by_user_id,
                            get_all_slugs_by_user_id, get_slugs_by_filters_from_db, delete_slug_by_admin_from_db,
                            slug_block_in_db)
from .shortener import generate_slug
from .exeptions import NoLongUrlFoundError, SlugAlreadyExistsError, SlugDoesntExistError


async def generate_rnd_short_url(
        url: str,
        user_id: str
) -> str:
    async def generate_slug_and_add_to_db():
        new_slug = generate_slug()
        await add_slug_to_db(new_slug, url, user_id)
        return new_slug
    for attempt in range(5):
        try:
            new_slug = await generate_slug_and_add_to_db()
            break
        except SlugAlreadyExistsError as ex:
            if attempt == 4:
                raise SlugAlreadyExistsError from ex
    return new_slug

async def get_url_by_slug(slug: str) -> str | None:
    long_url = await get_long_url_by_slug_from_db(slug)
    if not long_url:
        raise NoLongUrlFoundError()
    return long_url

async  def delete_slug(slug: str,
                       user_id: str):
    await delete_slug_by_user_id(slug, user_id)

async def get_user_slugs(user_id: str) -> list[dict]:
    slugs = await get_all_slugs_by_user_id(user_id)
    return [{"slug": s.slug, "long_url": s.long_url, "available": s.available} for s in slugs]

async def get_slugs_by_filters(slug: str | None = None, url: str | None = None, user_id: str | None = None) -> list[dict]:
    slugs = await get_slugs_by_filters_from_db(slug, url, user_id)
    return [{"slug": s.slug, "long_url": s.long_url, "user_id": s.user_id, "available": s.available} for s in slugs]

async def delete_slug_by_admin(slug: str):
    await delete_slug_by_admin_from_db(slug)

async def slug_block(slug):
    await slug_block_in_db(slug)