from typing import List

from fastapi import APIRouter, Depends
from flashcards_core.schedulers import get_available_schedulers
from flashcards_server.schemas import UserRead
from flashcards_server.users import current_active_user


router = APIRouter(
    prefix="/algorithms",
    tags=["algorithms"],
    # dependencies=[Depends(oauth2_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[str])
def get_algorithms(
    offset: int = 0, 
    limit: int = 100, 
    current_user: UserRead = Depends(current_active_user)
):
    return get_available_schedulers()
