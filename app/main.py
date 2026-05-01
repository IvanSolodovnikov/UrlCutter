from http.client import HTTPException

from fastapi import FastAPI, Depends, Body, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager

from .database.db import engine
from .database.models import Base
from .exeptions import NoLongUrlFoundError, SlugAlreadyExistsError, SlugNotAvailableError
from .service import generate_rnd_short_url, get_url_by_slug, delete_slug, get_user_slugs, get_slugs_by_filters, \
    delete_slug_by_admin, slug_block
from .dependencies.dependencies import get_or_create_user_id, get_current_admin
from .auth.routers import router as admin_login


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(admin_login)


@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    return FileResponse("app/static/index.html")


@app.post("/generate_short_url")
async def generate_short_url(url: str = Body(embed=True),
                             user_id: str = Depends(get_or_create_user_id)):
    try:
        new_slug = await generate_rnd_short_url(url, user_id)
    except SlugAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не удалось сгенерировать слаг")
    return {"data": new_slug}


@app.get("/my_slugs")
async def get_my_slugs(user_id: str = Depends(get_or_create_user_id)):
    return await get_user_slugs(user_id)

@app.get("/admin/search_slugs")
async def admin_get_slugs_by_filters(slug: str | None = None,
                                     url: str | None = None,
                                     user_id: str | None = None,
                                     admin_login: str = Depends(get_current_admin)):
    return await get_slugs_by_filters(slug, url, user_id)

@app.delete("/admin/delete_slug/{slug}")
async def admin_delete_slug(slug: str,
                            admin_login: str = Depends(get_current_admin)):
    await delete_slug_by_admin(slug)

@app.patch("/admin/slug_block")
async def admin_slug_block(slug: str,
                            admin_login: str = Depends(get_current_admin)):
    await slug_block(slug)

@app.delete("/delete_slug/{slug}")
async def delete_slug_by_user(slug: str,
    user_id: str = Depends(get_or_create_user_id)):
    await delete_slug(slug, user_id)


@app.get("/{slug}")
async def redirect_to_url(slug: str):
    try:
        long_url = await get_url_by_slug(slug)
    except NoLongUrlFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Ссылка не существует")
    except SlugNotAvailableError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Ссылка заблокирована")
    return RedirectResponse(url=long_url,
                            status_code=status.HTTP_302_FOUND)
