from typing import Any

from uuid import UUID
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from flashcards_core.schedulers import get_scheduler_for_deck

from flashcards_server.api import oauth2_scheme, get_session
from flashcards_server.api.decks import valid_deck
from flashcards_server.api.cards import Card, valid_card
from flashcards_server.api.auth import UserModel, get_current_user


class TestData(BaseModel):
    card_id: UUID
    result: Any


router = APIRouter(
    prefix="/study",
    tags=["study"],
    dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.post("/{deck_id}/next", response_model=Card)
def next_card(
    deck_id: UUID,
    test_data: TestData = Body(default=None),
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Processes the result of the previous test, if any, and returns the
    next card to study.

    :param deck_id: the deck being studied
    :param result: the result of the test (algorithm dependent)
    :returns: the next card to study
    """
    deck = valid_deck(session=session, user=current_user, deck_id=deck_id)
    scheduler = get_scheduler_for_deck(session=session, deck=deck)

    if test_data:
        card = valid_card(
            session=session,
            user=current_user,
            deck_id=deck_id,
            card_id=test_data.card_id,
        )
        scheduler.process_test_result(card=card, result=test_data.result)

    return scheduler.next_card()
