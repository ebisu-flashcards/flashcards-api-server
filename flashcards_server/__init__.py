from sqlalchemy.orm import Session
from passlib.context import CryptContext
from flashcards_core.database import init_db

from flashcards_server.auth.cookies import OAuth2PasswordBearerCookie
from flashcards_server.constants import (
    SQLALCHEMY_DATABASE_URL,
    SQLALCHEMY_DATABASE_CONNECTION_ARGS,
)

import importlib.metadata

__version__ = importlib.metadata.version("flashcards-server")


oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/auth/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_session() -> Session:
    """
    Allows other parts of the app to access the database properly
    FastAPI "Dependency" (used with Depends)
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


from flashcards_server.auth.models import DeckOwner, User  # noqa: F401, E402


SessionLocal = init_db(SQLALCHEMY_DATABASE_URL, SQLALCHEMY_DATABASE_CONNECTION_ARGS)
