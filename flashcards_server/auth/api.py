from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from flashcards_server.auth.functions import (
    get_session,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from flashcards_server.auth.schemas import User, Token
from flashcards_server.constants import ACCESS_TOKEN_EXPIRE_MINUTES


token_router = APIRouter(
    prefix="/token",
    tags=["token"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@token_router.post("/", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = authenticate_user(
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
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


users_router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@users_router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@users_router.get("/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]
