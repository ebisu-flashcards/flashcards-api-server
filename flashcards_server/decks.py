from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from flashcards_core.database import Deck as DeckModel

from flashcards_api.main import get_session


class DeckBase(BaseModel):
    name: str
    description: str
    state: str
    algorithm_id: int


class DeckCreate(DeckBase):
    pass


class Deck(DeckBase):
    id: int

    class Config:
        orm_mode = True


router = APIRouter(
    prefix="/decks",
    tags=["decks"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Deck])
def get_decks(
    offset: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    return DeckModel.get_all(session=session, offset=offset, limit=limit)


@router.get("/{deck_id}", response_model=Deck)
def get_deck(deck_id: int, session: Session = Depends(get_session)):
    session_deck = DeckModel.get_one(session=session, object_id=deck_id)
    if session_deck is None:
        raise HTTPException(
            status_code=404, detail=f"Deck with ID '{deck_id}' not found"
        )
    return session_deck


@router.post("/", response_model=Deck)
def create_deck(deck: DeckCreate, session: Session = Depends(get_session)):
    return DeckModel.create(session=session, **deck.dict())


@router.put("/{deck_id}", response_model=Deck)
def edit_deck(deck: DeckCreate, deck_id: int, session: Session = Depends(get_session)):
    return DeckModel.update(session=session, object_id=deck_id, **deck.dict())


@router.delete("/{deck_id}")
def delete_deck(deck_id: int, session: Session = Depends(get_session)):
    try:
        DeckModel.delete(session=session, object_id=deck_id)
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Deck with ID '{deck_id}' not found"
        )
