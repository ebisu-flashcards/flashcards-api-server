from fastapi import FastAPI, Request, Response
from flashcards_server.constants import DISPLAY_TRACEBACK_ON_500

# Create the FastAPI app
app = FastAPI()

# Import and include all routers
from flashcards_server.core_api.algorithms import (  # noqa: F401, E402
    router as algorithms_router,
)
from flashcards_server.core_api.cards import router as cards_router  # noqa: F401, E402
from flashcards_server.core_api.decks import router as decks_router  # noqa: F401, E402
from flashcards_server.core_api.facts import router as facts_router  # noqa: F401, E402
from flashcards_server.core_api.tags import router as tags_router  # noqa: F401, E402
from flashcards_server.auth.api import token_router, users_router  # noqa: F401, E402


app.include_router(algorithms_router)
app.include_router(cards_router)
app.include_router(decks_router)
app.include_router(facts_router)
app.include_router(tags_router)

app.include_router(token_router)
app.include_router(users_router)


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
