from typing import List

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from flashcards_server.database import (
    get_async_session,
    Tag as TagModel,
)


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: UUID

    class Config:
        orm_mode = True


router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    # dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[TagRead])
async def get_tags(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_async_session),
):
    return await TagModel.get_all_async(session=session, offset=offset, limit=limit)


@router.get("/{tag_id}", response_model=TagRead)
async def get_tag(
    tag_id: str,
    session: Session = Depends(get_async_session),
):
    return await TagModel.get_one_async(session=session, object_id=tag_id)


@router.post("/", response_model=TagRead)
async def create_tag(
    tag: TagCreate,
    session: Session = Depends(get_async_session),
):
    new_tag = await TagModel.create_async(session=session, **tag.dict())
    return new_tag

@router.patch("/{tag_id}", response_model=TagRead)
async def edit_tag(
    tag: TagCreate,
    tag_id: str,
    session: Session = Depends(get_async_session),
):
    db_tag = await TagModel.get_one_async(session=session, object_id=tag_id)
    return await TagModel.update_async(session=session, object_id=tag_id, **tag.dict())


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: str,
    session: Session = Depends(get_async_session),
):
    try:
        await TagModel.delete_async(session=session, object_id=tag_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Tag '{tag_id}' not found")
