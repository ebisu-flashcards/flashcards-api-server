from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from flashcards_core.database import Tag as TagModel

from flashcards_server.database import get_async_session


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    class Config:
        orm_mode = True


router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    # dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[TagRead])
def get_tags(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_async_session),
):
    return TagModel.get_all(session=session, offset=offset, limit=limit)


@router.get("/{tag_name}", response_model=TagRead)
def get_tag(
    tag_name: str,
    session: Session = Depends(get_async_session),
):
    db_tag = TagModel.get_by_name(session=session, name=tag_name)
    if db_tag is None:
        raise HTTPException(status_code=404, detail=f"Tag '{tag_name}' not found")
    return db_tag


@router.post("/", response_model=TagRead)
def create_tag(
    tag: TagCreate,
    session: Session = Depends(get_async_session),
):
    return TagModel.create(session=session, **tag.dict())


@router.patch("/{tag_name}", response_model=TagRead)
def edit_tag(
    tag: TagCreate,
    tag_name: str,
    session: Session = Depends(get_async_session),
):
    db_tag = TagModel.get_by_name(session=session, name=tag_name)
    return TagModel.update(session=session, object_id=db_tag.id, **tag.dict())


@router.delete("/{tag_name}")
def delete_tag(
    tag_name: str,
    session: Session = Depends(get_async_session),
):
    try:
        tag = TagModel.get_by_name(session=session, name=tag_name)
        TagModel.delete(session=session, object_id=tag.id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Tag '{tag_name}' not found")
