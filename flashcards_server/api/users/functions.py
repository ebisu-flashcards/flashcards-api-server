from typing import Optional

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from flashcards_server.api import get_session, oauth2_scheme, pwd_context
from flashcards_server.api.users.models import User as UserModel
from flashcards_server.constants import SECRET_KEY, HASHING_ALGORITHM


def authenticate(
    username: str, password: str, session: Session = Depends(get_session)
) -> Optional[UserModel]:
    """
    Given username and password, returns the user that matches, or None.
    Returns None also if the user exists, but is disabled.

    :param username: the user name
    :param password: the user's password in plaintext
    :param session: SQLAlchemy Session
    :return: the User (database model object) that can authenticate with these credentials.
    """
    db_user = UserModel.get_by_name(session=session, username=username)
    if not db_user or db_user.disabled:
        return None
    # Test the given password against the expected hash
    if not pwd_context.verify(password, db_user.hashed_password):
        return None
    return db_user


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> UserModel:
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
    except JWTError:
        raise unauthorized_exception

    # Get the user's row in the database - 401 if not found
    db_user = UserModel.get_by_name(session=session, username=username)
    if db_user is None:
        raise unauthorized_exception
    if db_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Returns the user
    return db_user
