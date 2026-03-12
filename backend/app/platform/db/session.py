from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.common.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)


def init_db() -> None:
    import app.platform.db.models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
