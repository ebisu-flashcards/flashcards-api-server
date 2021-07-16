from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from flashcards_core.database.algorithms import Algorithm as AlgorithmModel

from flashcards_api.main import get_db


class AlgorithmBase(BaseModel):
    name: str


class AlgorithmCreate(AlgorithmBase):
    pass


class Algorithm(AlgorithmBase):
    id: int

    class Config:
        orm_mode = True


router = APIRouter(
    prefix="/algorithms",
    tags=["algorithms"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[Algorithm])
def get_algorithms(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return AlgorithmModel.get_all(db=db, offset=offset, limit=limit)


@router.get("/{algorithm_id}", response_model=Algorithm)
def get_algorithm(algorithm_id: int, db: Session = Depends(get_db)):
    db_algorithm = AlgorithmModel.get_one(db=db, object_id=algorithm_id)
    if db_algorithm is None:
        raise HTTPException(status_code=404, detail=f"Algorithm ID '{algorithm_id}' not found")
    return db_algorithm


@router.post("/", response_model=Algorithm)
def create_algorithm(algorithm: AlgorithmCreate, db: Session = Depends(get_db)):
    return AlgorithmModel.create(db=db, **algorithm.dict())


@router.delete("/{algorithm_id}", response_model=Algorithm)
def delete_algorithm(algorithm_id: int, db: Session = Depends(get_db)):
    try:
        AlgorithmModel.delete(db=db, object_id=algorithm_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Algorithm ID '{algorithm_id}' not found")
