from typing import List, Optional

from uuid import UUID
from pydantic import BaseModel
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from flashcards_server.api import get_session, pwd_context
from flashcards_server.api.users.models import User as UserModel
from flashcards_server.api.users.functions import get_current_user
from flashcards_server.api.decks import Deck


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


router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=User)
async def create_new_user(
    username: str, email: str, password: str, session: Session = Depends(get_session)
):
    hashed_password = pwd_context.hash(password)
    return UserModel.create(
        session=session, username=username, email=email, hashed_password=hashed_password
    )


@router.get("/me", response_model=User)
async def get_my_details(current_user: UserModel = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=User)
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


@router.get("/me/decks/", response_model=List[Deck])
async def get_my_decks(
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return current_user.get_decks(session=session)


@router.delete("/me")
async def delete_my_user(
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    UserModel.delete(session=session, object_id=current_user.id)
