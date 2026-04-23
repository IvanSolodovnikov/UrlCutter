from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    url="postgresql+asyncpg://postgres:postgres@localhost:5433/postgres",
    pool_size=20,
    max_overflow=30,
)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)