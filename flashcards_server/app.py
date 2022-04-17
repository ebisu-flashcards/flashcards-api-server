from fastapi import FastAPI

#from flashcards_server import __version__
from flashcards_server.database import create_db_and_tables
from flashcards_server.users import auth_backend, fastapi_users


# Create the FastAPI app
app = FastAPI(
    title="Flashcards API",
    description="API Docs for flashcards-server",
    version="__version__",
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
app.include_router(fastapi_users.get_auth_router(auth_backend), tags=["auth"])
app.include_router(fastapi_users.get_register_router(), tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(), tags=["auth"])
app.include_router(fastapi_users.get_verify_router(), tags=["auth"])
app.include_router(fastapi_users.get_users_router(), prefix="/users", tags=["users"])


@app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()


# Default endpoint
@app.get("/")
async def root():
    return {"message": "Hello!"}
