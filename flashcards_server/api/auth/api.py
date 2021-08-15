from typing import Optional

from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from flashcards_server.api import get_session, pwd_context
from flashcards_server.api.auth.models import User as UserModel
from flashcards_server.api.auth.functions import (
    get_current_user,
    authenticate,
    create_access_token,
)
from flashcards_server.constants import ACCESS_TOKEN_EXPIRE_MINUTES


class UserBase(BaseModel):
    username: str
    email: str
    disabled: bool


class UserPatch(BaseModel):
    username: Optional[str]
    email: Optional[str]
    disabled: Optional[bool]


class User(UserBase):
    id: UUID

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", response_model=User)
async def create_new_user(
    username: str, email: str, password: str, session: Session = Depends(get_session)
):
    hashed_password = pwd_context.hash(password)
    return UserModel.create(
        session=session, username=username, email=email, hashed_password=hashed_password
    )


@router.post("/login", response_model=Token)
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


@router.get("/user", response_model=User)
async def get_my_details(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.patch("/user", response_model=User)
async def update_my_details(
    new_user_data: UserPatch,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    update_data = new_user_data.dict(exclude_unset=True)
    new_user_model = User(**vars(current_user)).copy(update=update_data)
    return UserModel.update(
        session=session, object_id=current_user.id, **new_user_model.dict()
    )


@router.delete("/user")
async def delete_my_user(
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    UserModel.delete(session=session, object_id=current_user.id)
