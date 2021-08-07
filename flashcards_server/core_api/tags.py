from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from flashcards_core.database import Tag as TagModel

from flashcards_server.auth.functions import get_session


class TagBase(BaseModel):
    name: str


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int

    class Config:
        orm_mode = True


router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Tag])
def get_tags(
    offset: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    return TagModel.get_all(session=session, offset=offset, limit=limit)


@router.get("/{tag_id}", response_model=Tag)
def get_tag(tag_id: int, session: Session = Depends(get_session)):
    session_tag = TagModel.get_one(session=session, object_id=tag_id)
    if session_tag is None:
        raise HTTPException(status_code=404, detail=f"Tag with ID '{tag_id}' not found")
    return session_tag


@router.post("/", response_model=Tag)
def create_tag(tag: TagCreate, session: Session = Depends(get_session)):
    return TagModel.create(session=session, **tag.dict())


@router.put("/{tag_id}", response_model=Tag)
def edit_tag(tag: TagCreate, tag_id: int, session: Session = Depends(get_session)):
    return TagModel.update(session=session, object_id=tag_id, **tag.dict())


@router.delete("/{tag_id}")
def delete_tag(tag_id: int, session: Session = Depends(get_session)):
    try:
        TagModel.delete(session=session, object_id=tag_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Tag with ID '{tag_id}' not found")
