from http.client import HTTPException
from typing import Annotated

from fastapi import FastAPI, Depends, Body, status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager

from pydantic import HttpUrl

from .database.db import engine
from .database.models import Base
from .exeptions import NoLongUrlFoundError, SlugAlreadyExistsError
from .service import generate_rnd_short_url, get_url_by_slug
from .dependencies.dependencies import get_or_create_user_id


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


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


@app.get("/{slug}")
async def redirect_to_url(slug: str):
    try:
        long_url = await get_url_by_slug(slug)
    except NoLongUrlFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Ссылка не существует")
    return RedirectResponse(url=long_url,
                            status_code=status.HTTP_302_FOUND)
