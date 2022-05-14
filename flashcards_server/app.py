import importlib.metadata

from fastapi import FastAPI
from fastapi.routing import APIRoute

from flashcards_server.database import create_db_and_tables
from flashcards_server.users import auth_backend, fastapi_users
from flashcards_server.schemas import UserRead, UserCreate, UserUpdate


__version__ = importlib.metadata.version('flashcards_server')


# Create the FastAPI app
app = FastAPI(
    title="Flashcards API",
    description="API Docs for flashcards-server",
    version=__version__,
)


# Import and include all routers
from flashcards_server.api.algorithms import (  # noqa: F401, E402
    router as algorithms_router,
)
from flashcards_server.api.cards import router as cards_router  # noqa: F401, E402
from flashcards_server.api.decks import router as decks_router  # noqa: F401, E402
from flashcards_server.api.facts import router as facts_router  # noqa: F401, E402
from flashcards_server.api.tags import router as tags_router  # noqa: F401, E402
from flashcards_server.api.study import router as study_router  # noqa: F401, E402

app.include_router(algorithms_router)
app.include_router(cards_router)
app.include_router(decks_router)
app.include_router(facts_router)
app.include_router(tags_router)
app.include_router(study_router)
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])  # Prefix needed for OpenAPI
app.include_router(fastapi_users.get_register_router(UserRead, UserCreate), tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead), tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate), prefix="/users", tags=["users"])


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()


# Default endpoint
@app.get("/")
async def root():
    return {"message": "Hello!"}



def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


use_route_names_as_operation_ids(app)