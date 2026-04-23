from .database.crud import add_slug_to_db, get_long_url_by_slug_from_db
from .shortener import generate_slug
from .exeptions import NoLongUrlFoundError, SlugAlreadyExistsError


async def generate_rnd_short_url(
        url: str
) -> str:
    async def generate_slug_and_add_to_db():
        slug = generate_slug()
        await add_slug_to_db(slug, url)
        return slug
    for attempt in range(5):
        try:
            slug = await generate_slug_and_add_to_db()
        except SlugAlreadyExistsError as ex:
            if attempt == 4:
                raise SlugAlreadyExistsError from ex
    return slug

async def get_url_by_slug(slug: str) -> str | None:
    long_url = await get_long_url_by_slug_from_db(slug)
    if not long_url:
        raise NoLongUrlFoundError()
    return long_url
