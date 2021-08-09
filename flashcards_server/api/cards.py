from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from flashcards_core.database import Card as CardModel

from flashcards_server.api import get_session


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


@router.get("/{card_id}", response_model=Card)
def get_card(card_id: int, session: Session = Depends(get_session)):
    session_card = CardModel.get_one(session=session, object_id=card_id)
    if session_card is None:
        raise HTTPException(
            status_code=404, detail=f"Card with ID '{card_id}' not found"
        )
    return session_card


@router.post("/", response_model=CardCreate)
def create_card(card: CardCreate, session: Session = Depends(get_session)):
    return CardModel.create(session=session, **card.dict())


@router.put("/{card_id}", response_model=Card)
def edit_card(card: CardCreate, card_id: int, session: Session = Depends(get_session)):
    return CardModel.update(session=session, object_id=card_id, **card.dict())


@router.delete("/{card_id}")
def delete_card(card_id: int, session: Session = Depends(get_session)):
    try:
        CardModel.delete(session=session, object_id=card_id)
    except ValueError:
        raise HTTPException(
            status_code=404, detail=f"Card with ID '{card_id}' not found"
        )
