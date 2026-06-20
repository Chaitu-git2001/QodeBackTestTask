from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app.models import backtest, stock, strategy  # noqa: F401
    from sqlalchemy import inspect

    inspector = inspect(engine)
    should_reset = False

    if inspector.has_table("stock_fundamentals"):
        columns = [c["name"] for c in inspector.get_columns("stock_fundamentals")]
        if "roce" not in columns:
            should_reset = True

    if inspector.has_table("backtests"):
        columns = [c["name"] for c in inspector.get_columns("backtests")]
        if "position_sizing" not in columns:
            should_reset = True

    if should_reset:
        print("Schema change detected. Re-creating tables...")
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
