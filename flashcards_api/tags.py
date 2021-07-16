from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from flashcards_core.database.tags import Tag as TagModel

from flashcards_api.main import get_db


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
def get_tags(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return TagModel.get_all(db=db, offset=offset, limit=limit)


@router.get("/{tag_id}", response_model=Tag)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = TagModel.get_one(db=db, object_id=tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail=f"Tag with ID '{tag_id}' not found")
    return db_tag


@router.post("/", response_model=Tag)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    return TagModel.create(db=db, **tag.dict())


@router.put("/{tag_id}", response_model=Tag)
def edit_tag(tag: TagCreate, tag_id: int, db: Session = Depends(get_db)):
    return TagModel.update(db=db, object_id=tag_id, **tag.dict())


@router.delete("/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    try:
        TagModel.delete(db=db, object_id=tag_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Tag with ID '{tag_id}' not found")
