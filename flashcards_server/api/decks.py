from typing import List, Optional

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from flashcards_core.database import Deck as DeckModel, Tag as TagModel

from flashcards_server import get_session, oauth2_scheme
from flashcards_server.auth import get_current_user, UserModel
from flashcards_server.api.tags import Tag, TagCreate


class DeckBase(BaseModel):
    name: str
    description: str
    algorithm: str


class DeckCreate(DeckBase):
    parameters: Optional[dict]
    tags: Optional[List[TagCreate]]


class DeckPatch(DeckCreate):
    name: Optional[str]
    description: Optional[str]
    algorithm: Optional[str]
    state: Optional[dict]


class Deck(DeckBase):
    id: UUID
    parameters: dict
    state: dict
    tags: List[Tag]

    class Config:
        orm_mode = True


def valid_deck(
    deck_id: UUID,
    user: UserModel,
    session: Session = Depends(get_session),
) -> DeckModel:
    """
    Check that the deck actually exists and belongs to the current user.

    :param deck_id: the ID of the deck to test.
    :returns: the deck object, if all checks passes.
    :raises: HTTPException is any check fails.
    """
    deck = DeckModel.get_one(session=session, object_id=deck_id)
    if not deck or not user.owns_deck(session=session, deck_id=deck_id):
        raise HTTPException(
            status_code=404, detail=f"Deck with ID '{deck_id}' not found"
        )
    return deck


router = APIRouter(
    prefix="/decks",
    tags=["decks"],
    dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=List[Deck])
async def get_my_decks(
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    return current_user.get_decks(session=session)


@router.get("/{deck_id}", response_model=Deck)
def get_deck(
    deck_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Get all the details of a deck.

    :param deck_id: the id of the deck to get
    :returns: The details of the deck. Cards list not included, use ``/deck/<uuid>/cards``
    """
    return valid_deck(session=session, user=current_user, deck_id=deck_id)


@router.post("/", response_model=Deck)
def create_deck(
    deck: DeckCreate,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Creates a new deck with the given data.

    :param deck: the details of the new deck.
    :returns: The new deck
    """
    deck_data = deck.dict()
    tags = deck_data.pop("tags", [])
    new_deck = current_user.create_deck(session=session, deck_data=deck_data)

    if tags:
        for tag in tags:
            tag_object = TagModel.get_by_name(session=session, name=tag["name"])
            if not tag_object:
                tag_object = TagModel.create(session=session, name=tag["name"])
            new_deck.assign_tag(session=session, tag_id=tag_object.id)

    return new_deck


@router.patch("/{deck_id}", response_model=Deck)
def edit_deck(
    deck_id: UUID,
    new_deck_data: DeckPatch,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Edits the details of the given deck

    :param deck_id: the id of the deck to be modified
    :param new_deck_data: the new details of the deck. Can be partial.
    :returns: The modified deck. Cards list not included, use ``/deck/<uuid>/cards``
    """
    deck_to_edit = valid_deck(session=session, user=current_user, deck_id=deck_id)

    update_data = new_deck_data.dict(exclude_unset=True)
    tags = update_data.pop("tags", [])

    new_deck_model = Deck(**vars(deck_to_edit)).copy(update=update_data)
    new_deck = DeckModel.update(
        session=session, object_id=deck_id, **new_deck_model.dict()
    )

    if tags:
        for tag in tags:
            tag_object = TagModel.get_by_name(session=session, name=tag["name"])
            if not tag_object:
                tag_object = TagModel.create(session=session, name=tag["name"])
            new_deck.assign_tag(session=session, tag_id=tag_object.id)

    return new_deck


@router.delete("/{deck_id}")
def delete_deck(
    deck_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Removes the given deck

    :param deck_id: the id of the deck to remove
    :returns: None
    """
    valid_deck(session=session, user=current_user, deck_id=deck_id)
    current_user.delete_deck(session=session, deck_id=deck_id)
