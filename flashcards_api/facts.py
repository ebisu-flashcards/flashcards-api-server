from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from flashcards_core.database.facts import Fact as FactModel

from flashcards_api.main import get_db


class FactBase(BaseModel):
    value: str


class FactCreate(FactBase):
    pass


class Fact(FactBase):
    id: int

    class Config:
        orm_mode = True


router = APIRouter(
    prefix="/facts",
    tags=["facts"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Fact])
def get_facts(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return FactModel.get_all(db=db, offset=offset, limit=limit)


@router.get("/{fact_id}", response_model=Fact)
def get_fact(fact_id: int, db: Session = Depends(get_db)):
    db_fact = FactModel.get_one(db=db, object_id=fact_id)
    if db_fact is None:
        raise HTTPException(status_code=404, detail=f"Fact with ID '{fact_id}' not found")
    return db_fact


@router.post("/", response_model=Fact)
def create_fact(fact: FactCreate, db: Session = Depends(get_db)):
    return FactModel.create(db=db, **fact.dict())


@router.put("/{fact_id}", response_model=FactCreate)
def edit_fact(fact: FactCreate, fact_id: int, db: Session = Depends(get_db)):
    return FactModel.update(db=db, object_id=fact_id, **fact.dict())


@router.delete("/{fact_id}")
def delete_fact(fact_id: int, db: Session = Depends(get_db)):
    try:
        FactModel.delete(db=db, object_id=fact_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Fact with ID '{fact_id}' not found")
