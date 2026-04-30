from .database.crud import (add_slug_to_db, get_long_url_by_slug_from_db, delete_slug_by_user_id,
                            get_all_slugs_by_user_id, get_all_slugs, get_slugs_by_url_from_db, get_slug_from_db,
                            get_slugs_by_user_id_from_db, get_slugs_by_filters_from_db)
from .database.models import ShortUrl
from .shortener import generate_slug
from .exeptions import NoLongUrlFoundError, SlugAlreadyExistsError, SlugDoesntExistError


async def generate_rnd_short_url(
        url: str,
        user_id: str
) -> str:
    async def generate_slug_and_add_to_db():
        slug = generate_slug()
        await add_slug_to_db(slug, url, user_id)
        return slug
    for attempt in range(5):
        try:
            slug = await generate_slug_and_add_to_db()
            break
        except SlugAlreadyExistsError as ex:
            if attempt == 4:
                raise SlugAlreadyExistsError from ex
    return slug

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
    return [{"slug": s.slug, "long_url": s.long_url} for s in slugs]


async def get_all_slugs_admin() -> list[dict]:
    slugs = await get_all_slugs()
    return [{"slug": s.slug, "long_url": s.long_url, "user_id": s.user_id} for s in slugs]

async def get_slug(slug:str) -> ShortUrl | None:
    slug = await get_slug_from_db(slug)
    if not slug:
        raise SlugDoesntExistError()
    return slug

async def get_slugs_by_url(url:str) -> list[dict] | None:
    slugs = await get_slugs_by_url_from_db(url)
    print(slugs[0].slug)
    if not slugs:
        raise SlugDoesntExistError()
    return [{"slug": s.slug, "long_url": s.long_url, "user_id": s.user_id} for s in slugs]

async def get_slugs_by_user_id(user_id: str) -> list[dict] | None:
    slugs = await get_slugs_by_user_id_from_db(user_id)
    if not slugs:
        raise SlugDoesntExistError()
    return [{"slug": s.slug, "long_url": s.long_url, "user_id": s.user_id} for s in slugs]

async def get_slugs_by_filters(slug: str, url: str, user_id: str) -> list[ShortUrl] | None:
    slugs = await get_slugs_by_filters_from_db(slug, url, user_id)
    if not slugs:
        raise SlugDoesntExistError()
    return [{"slug": s.slug, "long_url": s.long_url, "user_id": s.user_id} for s in slugs]