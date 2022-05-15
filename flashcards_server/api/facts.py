from typing import List, Optional

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from flashcards_server.database import (
    get_async_session,
    Fact as FactModel,
    Tag as TagModel,
)
from flashcards_server.users import current_active_user
from flashcards_server.schemas import UserRead
from flashcards_server.api.tags import TagRead, TagCreate


class FactBase(BaseModel):
    value: str
    format: str


class FactCreate(FactBase):
    tags: Optional[List[TagCreate]]
    related: Optional[List['FactBase']]


class FactPatch(BaseModel):
    value: Optional[str]
    format: Optional[str]


class RelatedFact(FactBase):
    id: UUID
    tags: List[TagRead]
    relationship: str

    class Config:
        orm_mode = True


class FactRead(FactBase):
    id: UUID
    tags: List[TagRead]
    related: Optional[List[RelatedFact]]

    class Config:
        orm_mode = True


router = APIRouter(
    prefix="/facts",
    tags=["facts"],
    # dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[FactRead])
async def get_facts(
    offset: int = 0,
    limit: int = 100,
    current_user: UserRead = Depends(current_active_user),  # to protect endpoint
    session: Session = Depends(get_async_session),
):
    """
    Get all facts.

    :returns: All the facts, paginated.
    """
    results: List[FactModel] = await FactModel.get_all_async(session=session, offset=offset, limit=limit)
    db_facts = []
    for db_fact in results:
        db_fact.related = await db_fact.related_facts_async(session)
        db_facts.append(db_fact)
    return db_facts


@router.get("/{fact_id}", response_model=FactRead)
async def get_fact(
    fact_id: UUID,
    current_user: UserRead = Depends(current_active_user),  # to protect endpoint
    session: Session = Depends(get_async_session),
):
    """
    Get all the details of one fact.

    :param fact_id: the id of the fact to get
    :returns: The details of the fact.
    """
    db_fact: FactModel = await FactModel.get_one_async(session=session, object_id=fact_id)
    db_fact.related = await db_fact.related_facts_async(session)
    if db_fact is None:
        raise HTTPException(
            status_code=404, detail=f"Fact with ID '{fact_id}' not found"
        )
    return db_fact


@router.get("/tag/{tag_name}", response_model=List[FactRead])
async def get_facts_by_tag(
    tag_name: str,
    offset: int = 0,
    limit: int = 100,
    current_user: UserRead = Depends(current_active_user),  # to protect endpoint
    session: Session = Depends(get_async_session),
):
    """
    Get all the details of the facts which have this tag assigned.

    :param tag_name: the name of the tag to filter facts on
    :param offset: for pagination, index at which to start returning values.
    :param limit: for pagination, maximum number of elements to return.
    :returns: The list of facts with this tag.
    """
    stmt = (
        select(FactModel)
        .where(FactModel.tags.any(TagModel.name == tag_name))
        .offset(offset)
        .limit(limit)
    )
    results = await session.scalars(stmt)
    db_facts = []
    for db_fact in results:
        db_fact.related = await db_fact.related_facts_async(session)
        db_facts.append(db_fact)
    return results.all()


@router.post("/", response_model=FactRead)
async def create_fact(
    fact: FactCreate,
    current_user: UserRead = Depends(current_active_user),  # to protect endpoint
    session: Session = Depends(get_async_session),
):
    """
    Creates a new fact with the given data.

    :param fact: the details of the new fact.
    :returns: The new fact
    """
    fact_data = fact.dict()
    tags = fact_data.pop("tags", [])
    new_fact = await FactModel.create_async(session=session, **fact_data)

    for tag in tags:
        tag_object = await TagModel.get_by_name_async(session=session, name=tag["name"])
        if not tag_object:
            tag_object = await TagModel.create_async(session=session, name=tag["name"])
        await new_fact.assign_tag_async(session=session, tag_id=tag_object.id)
    return new_fact


@router.patch("/{fact_id}", response_model=FactRead)
async def edit_fact(
    fact_id: UUID,
    new_fact_data: FactPatch,
    current_user: UserRead = Depends(current_active_user),  # to protect endpoint
    session: Session = Depends(get_async_session),
):
    """
    Edits the details of the given fact

    :param fact_id: the id of the fact to edit
    :param new_fact_data: the new details of the fact. Can be partial.
    :returns: The modified fact
    """
    update_data = new_fact_data.dict(exclude_unset=True)
    original_data = await get_fact(fact_id=fact_id, current_user=current_active_user, session=session)
    new_model = FactBase(**original_data).copy(update=update_data)
    new_fact = await FactModel.update(session=session, object_id=fact_id, **new_model.dict())
    return new_fact


@router.put("/{fact_id}/tags/{tag_name}", response_model=FactRead)
async def assign_tag_to_fact(
    fact_id: UUID,
    tag_name: str,
    current_user: UserRead = Depends(current_active_user),  # to protect endpoint
    session: Session = Depends(get_async_session),
):
    """
    Assign this tag to the fact.

    :param fact_id: the id of the fact to edit
    :param tag_name: the tag to assign to this fact
    :returns: The modified fact
    """
    fact = await FactModel.get_one_async(session=session, object_id=fact_id)
    tag = await TagModel.get_by_name_async(session=session, name=tag_name)
    if not tag:
        tag = await TagModel.create_async(session=session, name=tag_name)
    await fact.assign_tag_async(session=session, tag_id=tag.id)

    fact = await get_fact(fact_id=fact_id, current_user=current_active_user, session=session)
    return fact


@router.delete("/{fact_id}/tags/{tag_name}", response_model=FactRead)
async def remove_tag_from_fact(
    fact_id: UUID,
    tag_name: str,
    current_user: UserRead = Depends(current_active_user),  # to protect endpoint
    session: Session = Depends(get_async_session),
):
    """
    Remove this tag from the fact.

    :param fact_id: the id of the fact to edit
    :param tag_name: the tag to remove from this fact
    :returns: The modified fact
    """
    fact = await FactModel.get_one_async(session=session, object_id=fact_id)
    tag = await TagModel.get_by_name_async(session=session, name=tag_name)
    if not tag:
        raise HTTPException(status_code=404, detail=f"Tag '{tag_name}' doesn't exist.")
    await fact.remove_tag_async(session=session, tag_id=tag.id)

    fact = await get_fact(fact_id=fact_id, current_user=current_active_user, session=session)
    return fact

@router.put("/{fact_id}/related/", response_model=FactRead)
async def assign_related_fact(
    fact_id: UUID,
    related_fact_id: str,
    relationship: str,
    current_user: UserRead = Depends(current_active_user),  # to protect endpoint
    session: Session = Depends(get_async_session),
):
    """
    Assign a related fact to the fact.

    :param fact_id: the id of the fact to edit
    :param related_fact_id: the related fact to assign to this fact
    :param relationship: the type of relationship between these cards
    :returns: The modified fact
    """
    fact: FactModel = await FactModel.get_one_async(session=session, object_id=fact_id)
    await fact.assign_related_fact_async(session=session, fact_id=related_fact_id, relationship=relationship)
    fact = await get_fact(fact_id=fact_id, current_user=current_active_user, session=session)
    return fact


@router.delete("/{fact_id}/related/", response_model=FactRead)
async def remove_related_fact(
    fact_id: UUID,
    related_fact_id: str,
    relationship: str,
    current_user: UserRead = Depends(current_active_user),  # to protect endpoint
    session: Session = Depends(get_async_session),
):
    """
    Remove the relationship between these two facts.

    :param fact_id: the id of the fact to edit
    :param related_fact_id: the related fact to assign to this fact
    :returns: The modified fact
    """
    fact: FactModel = await FactModel.get_one_async(session=session, object_id=fact_id)
    await fact.remove_related_fact_async(session=session, fact_id=related_fact_id, relationship=relationship)
    fact = await get_fact(fact_id=fact_id, current_user=current_active_user, session=session)
    return fact


@router.delete("/{fact_id}")
async def delete_fact(
    fact_id: str,
    current_user: UserRead = Depends(current_active_user),  # to protect endpoint
    session: Session = Depends(get_async_session),
):
    try:
        await FactModel.delete_async(session=session, object_id=fact_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Fact '{fact_id}' not found")