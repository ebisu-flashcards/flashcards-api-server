from typing import Optional

from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from flashcards_core.database import init_db

from flashcards_server.auth.models import User as UserModel
from flashcards_server.auth.schemas import User, UserInDB, TokenData
from flashcards_server.constants import (
    SQLALCHEMY_DATABASE_URL,
    SQLALCHEMY_DATABASE_CONNECTION_ARGS,
    SECRET_KEY,
    HASHING_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SessionLocal = init_db(SQLALCHEMY_DATABASE_URL, SQLALCHEMY_DATABASE_CONNECTION_ARGS)


# Allow other parts of the app to access the database properly
# FastAPI "Dependency" (used with Depends)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def authenticate_user(
    username: str, password: str, session: Session
) -> Optional[UserInDB]:
    """
    Given username and password, returns the user that matches, or None.

    :param username: the user name
    :param password: the user's password in plaintext
    :param session: SQLAlchemy Session
    :return: the User (database model object) that can authenticate with these credentials.
    """
    db_user = session.query(UserModel).filter(UserModel.username == username).first()
    if not db_user:
        return None

    # Test the given password against the expected hash
    if not pwd_context.verify(password, db_user.hashed_password):
        return None

    return UserInDB(**vars(db_user))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT token with the given data.

    :param data: the information to encode in the JWT
    :param expires_delta: the expiration time delta. If None, uses `ACCESS_TOKEN_EXPIRE_MINUTES`
    :return: the encoded JWT
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=HASHING_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> UserInDB:
    """
    Gets the data of the user which is currently logged in, according to the token.

    :param token: the JWT token of the user
    :return: the user this token belongs to
    """
    # Definition of the exception  #FIXME can be moved out of here?
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the JWT - 401 if malformed
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[HASHING_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise unauthorized_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise unauthorized_exception

    # Get the user's row in the database - 401 if not found
    db_user = (
        session.query(UserModel)
        .filter(UserModel.username == token_data.username)
        .first()
    )
    if db_user is None:
        raise unauthorized_exception
    return UserInDB(**vars(db_user))


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> UserInDB:
    """
    Gets the data of the user which is currently logged in, according to the token,
    if the user is not disabled. Raises a 401 otherwise.

    :param token: the JWT token of the user
    :return: the user this token belongs to
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
