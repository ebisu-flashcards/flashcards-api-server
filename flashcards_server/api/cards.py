from typing import List, Optional

from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from flashcards_core.database import (
    Card as CardModel,
    Tag as TagModel,
    Fact as FactModel,
)

from flashcards_server.api import get_session, oauth2_scheme
from flashcards_server.api.decks import router, deck_exists
from flashcards_server.api.facts import Fact
from flashcards_server.api.tags import Tag, TagCreate


class CardCreate(BaseModel):
    question_id: UUID
    answer_id: UUID
    question_context_facts: Optional[List[UUID]]
    answer_context_facts: Optional[List[UUID]]
    tags: Optional[List[TagCreate]]


class CardPatch(BaseModel):
    question_id: Optional[UUID]
    answer_id: Optional[UUID]


class Card(BaseModel):
    id: UUID
    deck_id: UUID
    question: Fact
    answer: Fact
    question_context_facts: List[Fact]
    answer_context_facts: List[Fact]
    tags: List[Tag]

    class Config:
        orm_mode = True


def card_exists_in_deck(session: Session, deck_id: UUID, card_id: UUID) -> CardModel:
    """
    Check that the card actually exists and belongs to the given deck.
    """
    deck_exists(session=session, deck_id=deck_id)
    card = CardModel.get_one(session=session, object_id=card_id)
    if card is None or card.deck_id != deck_id:
        raise HTTPException(
            status_code=404, detail=f"Card with ID '{card_id}' not found"
        )
    return card


@router.get("/{deck_id}/cards", response_model=List[Card])
def get_cards(
    deck_id: UUID,
    offset: int = 0,
    limit: int = 100,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Get all the cards for a deck (paginated, if needed).

    :param deck_id: the id of the deck this card belongs to
    :param offset: for pagination, index at which to start returning cards.
    :param limit: for pagination, maximum number of cards to return.
    :returns: List of cards.
    """
    deck_exists(session=session, deck_id=deck_id)
    db_cards = (
        session.query(CardModel)
        .filter(CardModel.deck_id == deck_id)
        .offset(offset)
        .limit(limit)
        .all()
    )
    return db_cards


@router.get("/{deck_id}/cards/{card_id}", response_model=Card)
def get_card(
    deck_id: UUID,
    card_id: UUID,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Get all the details of one card.

    :param deck_id: the id of the deck this card belongs to
    :param card_id: the id of the card to get
    :returns: The details of the card.
    """
    card = card_exists_in_deck(session=session, deck_id=deck_id, card_id=card_id)
    return card


@router.post("/{deck_id}/cards", response_model=Card)
def create_card(
    deck_id: UUID,
    card: CardCreate,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Creates a new card with the given data.

    :param deck_id: the id of the deck this card will belong to
    :param card: the details of the new card.
    :returns: The new card
    """
    deck_exists(session=session, deck_id=deck_id)

    card_data = card.dict()
    card_data["deck_id"] = deck_id
    tags = card_data.pop("tags", [])
    question_context = card_data.pop("question_context_facts", [])
    answer_context = card_data.pop("answer_context_facts", [])
    new_card = CardModel.create(session=session, **card_data)

    if tags:
        for tag in tags:
            tag_object = TagModel.get_by_name(session=session, name=tag["name"])
            if not tag_object:
                tag_object = TagModel.create(session=session, name=tag["name"])
            new_card.assign_tag(session=session, tag_id=tag_object.id)

    if question_context:
        for fact in question_context:
            fact_object = FactModel.get_one(session=session, object_id=fact)
            if not fact_object:
                raise HTTPException(
                    status_code=404, detail=f"Fact with ID '{fact}' not found"
                )
            new_card.assign_question_context(session=session, fact_id=fact)

    if answer_context:
        for fact in answer_context:
            fact_object = FactModel.get_one(session=session, object_id=fact)
            if not fact_object:
                raise HTTPException(
                    status_code=404, detail=f"Fact with ID '{fact}' not found"
                )
            new_card.assign_answer_context(session=session, fact_id=fact)

    return new_card


@router.patch("/{deck_id}/cards/{card_id}", response_model=Card)
def edit_card(
    deck_id: UUID,
    card_id: UUID,
    new_card_data: CardPatch,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Edits the details of the given card

    :param deck_id: the id of the deck this card belongs to
    :param card_id: the id of the card to edit
    :param new_card_data: the new details of the card. Can be partial.
    :returns: The modified card
    """
    original_data = card_exists_in_deck(
        session=session, deck_id=deck_id, card_id=card_id
    )

    update_data = new_card_data.dict(exclude_unset=True)
    new_model = CardCreate(**vars(original_data)).copy(update=update_data)
    new_model_data = {
        key: value for key, value in new_model.dict().items() if value is not None
    }
    CardModel.update(session=session, object_id=card_id, **new_model_data)
    return CardModel.get_one(session=session, object_id=card_id)


@router.put("/{deck_id}/cards/{card_id}/tags/{tag_name}", response_model=Card)
def assign_tag_to_card(
    deck_id: UUID,
    card_id: UUID,
    tag_name: str,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Assign this tag to the card.

    :param deck_id: the id of the deck this card belongs to
    :param card_id: the id of the card to edit
    :param tag_name: the tag to assign to this card
    :returns: The modified card
    """
    card = card_exists_in_deck(session=session, deck_id=deck_id, card_id=card_id)
    tag = TagModel.get_by_name(session=session, name=tag_name)
    if not tag:
        tag = TagModel.create(session=session, name=tag_name)
    card.assign_tag(session=session, tag_id=tag.id)


@router.delete("/{deck_id}/cards/{card_id}/tags/{tag_name}", response_model=Card)
def remove_tag_from_card(
    deck_id: UUID,
    card_id: UUID,
    tag_name: str,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Remove this tag from the card.

    :param deck_id: the id of the deck this card belongs to
    :param card_id: the id of the card to edit
    :param tag_name: the tag to remove from this card
    :returns: The modified card
    """
    card = card_exists_in_deck(session=session, deck_id=deck_id, card_id=card_id)
    tag = TagModel.get_by_name(session=session, name=tag_name)
    if not tag:
        raise HTTPException(status_code=404, detail=f"Tag '{tag_name}' doesn't exist.")
    card.remove_tag(session=session, tag_id=tag.id)


@router.put(
    "/{deck_id}/cards/{card_id}/context/question/{fact_id}", response_model=Card
)
def assign_question_context_to_card(
    deck_id: UUID,
    card_id: UUID,
    fact_id: UUID,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Assign this fact as a context for the question of the card.

    :param deck_id: the id of the deck this card belongs to
    :param card_id: the id of the card to edit
    :param fact_id: the fact to assign as question context to this card
    :returns: The modified card
    """
    card = card_exists_in_deck(session=session, deck_id=deck_id, card_id=card_id)
    fact = FactModel.get_one(session=session, object_id=fact_id)
    if not fact:
        raise HTTPException(
            status_code=404, detail=f"Fact with ID '{fact_id}' doesn't exist."
        )
    card.assign_question_context(session=session, fact_id=fact.id)


@router.delete(
    "/{deck_id}/cards/{card_id}/context/question/{fact_id}", response_model=Card
)
def remove_question_context_from_card(
    deck_id: UUID,
    card_id: UUID,
    fact_id: UUID,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Remove this fact from the question context of the card.

    :param deck_id: the id of the deck this card belongs to
    :param card_id: the id of the card to edit
    :param fact_id: the id of the fact to remove from the question context
    :returns: The modified card
    """
    card = card_exists_in_deck(session=session, deck_id=deck_id, card_id=card_id)
    fact = FactModel.get_one(session=session, object_id=fact_id)
    if not fact:
        raise HTTPException(
            status_code=404, detail=f"Fact with ID '{fact_id}' doesn't exist."
        )
    card.remove_question_context(session=session, fact_id=fact.id)


@router.put("/{deck_id}/cards/{card_id}/context/answer/{fact_id}", response_model=Card)
def assign_answer_context_to_card(
    deck_id: UUID,
    card_id: UUID,
    fact_id: UUID,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Assign this fact as a context for the answer of the card.

    :param deck_id: the id of the deck this card belongs to
    :param card_id: the id of the card to edit
    :param fact_id: the fact to assign as answer context to this card
    :returns: The modified card
    """
    card = card_exists_in_deck(session=session, deck_id=deck_id, card_id=card_id)
    fact = FactModel.get_one(session=session, object_id=fact_id)
    if not fact:
        raise HTTPException(
            status_code=404, detail=f"Fact with ID '{fact_id}' doesn't exist."
        )
    card.assign_answer_context(session=session, fact_id=fact.id)


@router.delete(
    "/{deck_id}/cards/{card_id}/context/answer/{fact_id}", response_model=Card
)
def remove_answer_context_from_card(
    deck_id: UUID,
    card_id: UUID,
    fact_id: UUID,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Remove this fact from the answer context of the card.

    :param deck_id: the id of the deck this card belongs to
    :param card_id: the id of the card to edit
    :param fact_id: the id of the fact to remove from the answer context
    :returns: The modified card
    """
    card = card_exists_in_deck(session=session, deck_id=deck_id, card_id=card_id)
    fact = FactModel.get_one(session=session, object_id=fact_id)
    if not fact:
        raise HTTPException(
            status_code=404, detail=f"Fact with ID '{fact_id}' doesn't exist."
        )
    card.remove_answer_context(session=session, fact_id=fact.id)


@router.delete("/{deck_id}/cards/{card_id}")
def delete_card(
    deck_id: UUID,
    card_id: UUID,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    """
    Removes the given card from this deck

    :param deck_id: the id of the deck to remove the card from
    :param card_id: the id of the card to delete
    :returns: None
    """
    card_exists_in_deck(session=session, deck_id=deck_id, card_id=card_id)
    CardModel.delete(session=session, object_id=card_id)