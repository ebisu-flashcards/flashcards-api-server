from typing import Optional

from datetime import datetime, timedelta
from jose import jwt
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from flashcards_server.api import get_session
from flashcards_server.api.users import authenticate
from flashcards_server.constants import (
    SECRET_KEY,
    HASHING_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


router = APIRouter(
    prefix="/token",
    tags=["token"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = authenticate(
        username=form_data.username, password=form_data.password, session=session
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data_to_encode={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def create_access_token(
    data_to_encode: dict, expires_delta: Optional[timedelta] = None
):
    """
    Create a JWT token with the given data.

    :param data_to_encode: the information to encode in the JWT
    :param expires_delta: the expiration time delta. If None, uses `ACCESS_TOKEN_EXPIRE_MINUTES`
    :return: the encoded JWT
    """
    to_encode = data_to_encode.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=HASHING_ALGORITHM)
    return encoded_jwt
