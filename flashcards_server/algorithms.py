from typing import List

from fastapi import APIRouter
from flashcards_core.schedulers import get_available_schedulers


router = APIRouter(
    prefix="/algorithms",
    tags=["algorithms"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[str])
def get_algorithms(offset: int = 0, limit: int = 100):
    return get_available_schedulers()
