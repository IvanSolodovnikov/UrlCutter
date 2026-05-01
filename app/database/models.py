from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column



class Base(DeclarativeBase):
    ...


class ShortUrl(Base):
    __tablename__ = "short_urls"

    slug: Mapped[str] = mapped_column(primary_key=True)
    long_url: Mapped[str] =  mapped_column(nullable=False)
    user_id: Mapped[str] =  mapped_column(nullable=False)
    available: Mapped[bool] = mapped_column(nullable=False, default=True)

class Admin(Base):
    __tablename__ = "admins"

    login: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(nullable=False)
