from typing import List, Optional

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from flashcards_core.database import Deck as DeckModel

from flashcards_server.api import get_session, oauth2_scheme
from flashcards_server.api.users import get_current_user, UserModel


class DeckBase(BaseModel):
    name: str
    description: str
    algorithm: str


class DeckCreate(DeckBase):
    pass


class DeckPatch(BaseModel):
    name: Optional[str]
    description: Optional[str]
    algorithm: Optional[str]
    parameters: Optional[dict]
    state: Optional[dict]


class Deck(DeckBase):
    id: UUID
    parameters: dict
    state: dict
    tags: List[str]

    class Config:
        orm_mode = True


router = APIRouter(
    prefix="/decks",
    tags=["decks"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/{deck_id}", response_model=Deck)
def get_deck(
    deck_id: UUID,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    session_deck = DeckModel.get_one(session=session, object_id=deck_id)
    if session_deck is None:
        raise HTTPException(
            status_code=404, detail=f"Deck with ID '{deck_id}' not found"
        )
    return session_deck


@router.post("/", response_model=Deck)
def create_deck(
    deck: DeckCreate,
    token: str = Depends(oauth2_scheme),
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    new_deck = current_user.create_deck(session=session, deck_data=deck.dict())
    return new_deck


@router.patch("/{deck_id}", response_model=Deck)
def edit_deck(
    deck_id: UUID,
    new_deck_data: DeckPatch,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    update_data = new_deck_data.dict(exclude_unset=True)
    deck_to_edit = DeckModel.get_one(session=session, object_id=deck_id)
    new_deck_model = Deck(**vars(deck_to_edit)).copy(update=update_data)
    return DeckModel.update(session=session, object_id=deck_id, **new_deck_model.dict())


@router.delete("/{deck_id}")
def delete_deck(
    deck_id: UUID,
    token: str = Depends(oauth2_scheme),
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    try:
        current_user.create_deck(session=session, deck_id=deck_id)
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Deck with ID '{deck_id}' not found"
        )
