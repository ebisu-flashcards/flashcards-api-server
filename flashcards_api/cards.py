from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from flashcards_core.database.cards import Card as CardModel
from flashcards_api.main import get_db


class CardBase(BaseModel):
    deck_id: int


class CardCreate(CardBase):
    pass


class Card(CardBase):
    id: int

    class Config:
        orm_mode = True


router = APIRouter(
    prefix="/cards",
    tags=["cards"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Card])
def get_cards(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CardModel.get_all(db=db, offset=offset, limit=limit)


@router.get("/{card_id}", response_model=Card)
def get_card(card_id: int, db: Session = Depends(get_db)):
    db_card = CardModel.get_one(db=db, object_id=card_id)
    if db_card is None:
        raise HTTPException(status_code=404, detail=f"Card with ID '{card_id}' not found")
    return db_card


@router.post("/", response_model=CardCreate)
def create_card(card: CardCreate, db: Session = Depends(get_db)):
    return CardModel.create(db=db, **card.dict())


@router.put("/{card_id}", response_model=Card)
def edit_card(card: CardCreate, card_id: int, db: Session = Depends(get_db)):
    return CardModel.update(db=db, object_id=card_id, **card.dict())


@router.delete("/{card_id}")
def delete_card(card_id: int, db: Session = Depends(get_db)):
    try:
        CardModel.delete(db=db, object_id=card_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Card with ID '{card_id}' not found")
