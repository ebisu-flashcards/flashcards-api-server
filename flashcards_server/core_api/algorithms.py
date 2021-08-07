from typing import List

from fastapi import APIRouter, Depends
from flashcards_core.schedulers import get_available_schedulers

from flashcards_server.auth.functions import oauth2_scheme


router = APIRouter(
    prefix="/algorithms",
    tags=["algorithms"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[str])
def get_algorithms(
    token: str = Depends(oauth2_scheme), offset: int = 0, limit: int = 100
):
    return get_available_schedulers()
