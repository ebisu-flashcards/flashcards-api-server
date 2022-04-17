from typing import Any

from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from flashcards_core.schedulers import get_scheduler_for_deck

from flashcards_server.database import get_async_session

# from flashcards_server.auth import oauth2_scheme
from flashcards_server.api.decks import valid_deck
from flashcards_server.api.cards import Card, valid_card
from flashcards_server.users import current_active_user
from flashcards_server.models import User as UserModel


class TestData(BaseModel):
    card_id: UUID
    result: Any


router = APIRouter(
    prefix="/study",
    tags=["study"],
    # dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.get("/{deck_id}/start", response_model=Card)
def first_card(
    deck_id: UUID,
    current_user: UserModel = Depends(current_active_user),
    session: Session = Depends(get_async_session),
):
    """
    Get the first card to study.

    :param deck_id: the deck being studied
    :returns: the next card to study
    """
    deck = valid_deck(session=session, user=current_user, deck_id=deck_id)
    scheduler = get_scheduler_for_deck(session=session, deck=deck)
    return scheduler.next_card()


@router.post("/{deck_id}/next", response_model=Card)
def next_card(
    deck_id: UUID,
    test_data: TestData,
    current_user: UserModel = Depends(current_active_user),
    session: Session = Depends(get_async_session),
):
    """
    Processes the result of the previous test and returns the
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
