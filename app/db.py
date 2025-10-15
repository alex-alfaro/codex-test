from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./marketplace.db"

engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)


def init_db() -> None:
    """Create database tables."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def session_scope() -> Iterator[Session]:
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Iterator[Session]:
    with session_scope() as session:
        yield session
