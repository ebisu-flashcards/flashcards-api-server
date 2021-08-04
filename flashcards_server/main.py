from fastapi import FastAPI, Request, Response
from flashcards_core.database import init_db

from flashcards_server.constants import (
    SQLALCHEMY_DATABASE_URL,
    SQLALCHEMY_DATABASE_CONNECTION_ARGS,
    DISPLAY_TRACEBACK_ON_500,
)


SessionLocal = init_db(SQLALCHEMY_DATABASE_URL, SQLALCHEMY_DATABASE_CONNECTION_ARGS)


# Allow other parts of the app to access the database properly
# FastAPI "Dependency" (used with Depends)
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# Create the FastAPI app
app = FastAPI()


# Import and include all routers
from flashcards_server.algorithms import router as algorithms_router  # noqa: F401, E402
from flashcards_server.cards import router as cards_router  # noqa: F401, E402
from flashcards_server.decks import router as decks_router  # noqa: F401, E402
from flashcards_server.facts import router as facts_router  # noqa: F401, E402
from flashcards_server.tags import router as tags_router  # noqa: F401, E402


app.include_router(algorithms_router)
app.include_router(cards_router)
app.include_router(decks_router)
app.include_router(facts_router)
app.include_router(tags_router)


# Default endpoint
@app.get("/")
async def root():
    return {"message": "Hello Reader!"}


# Debug 500 handler to display the tracebacks in the returned message
if DISPLAY_TRACEBACK_ON_500:

    @app.exception_handler(Exception)
    async def debug_exception_handler(request: Request, exc: Exception):
        import traceback

        return Response(
            status_code=500,
            media_type="text/plain",
            content="".join(
                traceback.format_exception(
                    etype=type(exc), value=exc, tb=exc.__traceback__
                )
            ),
        )
