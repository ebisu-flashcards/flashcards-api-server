from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from flashcards_core.database.decks import Deck as DeckModel

from flashcards_api.main import get_db


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
def get_decks(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return DeckModel.get_all(db=db, offset=offset, limit=limit)


@router.get("/{deck_id}", response_model=Deck)
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    db_deck = DeckModel.get_one(db=db, object_id=deck_id)
    if db_deck is None:
        raise HTTPException(status_code=404, detail=f"Deck with ID '{deck_id}' not found")
    return db_deck


@router.post("/", response_model=Deck)
def create_deck(deck: DeckCreate, db: Session = Depends(get_db)):
    return DeckModel.create(db=db, **deck.dict())


@router.put("/{deck_id}", response_model=Deck)
def edit_deck(deck: DeckCreate, deck_id: int, db: Session = Depends(get_db)):
    return DeckModel.update(db=db, object_id=deck_id, **deck.dict())


@router.delete("/{deck_id}")
def delete_deck(deck_id: int, db: Session = Depends(get_db)):
    try:
        DeckModel.delete(db=db, object_id=deck_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Deck with ID '{deck_id}' not found")
