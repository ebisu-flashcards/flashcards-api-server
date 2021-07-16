from fastapi import FastAPI, Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from flashcards_api.constants import SQLALCHEMY_DATABASE_URL, DISPLAY_TRACEBACK_ON_500


# Create database connection
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed only for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Allow other parts of the app to access the db instance properly
# FastAPI "Dependency" (used with Depends)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create the FastAPI app
app = FastAPI()


# Import and include all routers
from flashcards_api.algorithms import router as algorithms_router
from flashcards_api.cards import router as cards_router
from flashcards_api.decks import router as decks_router
from flashcards_api.facts import router as facts_router
from flashcards_api.tags import router as tags_router


app.include_router(algorithms_router)
app.include_router(cards_router)
app.include_router(decks_router)
app.include_router(facts_router)
app.include_router(tags_router)


# Default endpoint
@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}


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
            )
        )
