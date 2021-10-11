from sqlalchemy.orm import Session
from flashcards_core.database import init_db
from flashcards_server.constants import (
    SQLALCHEMY_DATABASE_URL,
    SQLALCHEMY_DATABASE_CONNECTION_ARGS,
)
from flashcards_server.models import DeckOwner, User  # noqa: F401


session_local = init_db(SQLALCHEMY_DATABASE_URL, SQLALCHEMY_DATABASE_CONNECTION_ARGS)


def get_session() -> Session:
    """
    Allows other parts of the app to access the database properly
    FastAPI "Dependency" (used with Depends)
    """
    session = session_local()
    try:
        yield session
    finally:
        session.close()
