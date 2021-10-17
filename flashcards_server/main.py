from fastapi import FastAPI, Request, Response

from flashcards_server import __version__ as version
from flashcards_server.constants import DISPLAY_TRACEBACK_ON_500

# from flashcards_server.database import database
# from flashcards_server.models import UserDB
from flashcards_server.users import users, cookie_authentication


# Create the FastAPI app
app = FastAPI(
    title="Flashcards API",
    description="API Docs for flashcards-server",
    version=version,
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


# # Override a few methods to allow login by username
# users_router = users.get_users_router()

# @users_router.post(
#     "/register", response_model=user_model, status_code=status.HTTP_201_CREATED
# )
# async def register(request: Request, user: user_create_model):  # type: ignore
#     user = cast(models.BaseUserCreate, user)  # Prevent mypy complain
#     existing_user = await user_db.get_by_email(user.email)

#     if existing_user is not None:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
#         )

#     hashed_password = get_password_hash(user.password)
#     db_user = user_db_model(
#         **user.create_update_dict(), hashed_password=hashed_password
#     )
#     created_user = await user_db.create(db_user)

#     await router.run_handlers(Event.ON_AFTER_REGISTER, created_user, request)

#     return created_user


# Add authentication routers from fastapi-users
app.include_router(
    users.get_auth_router(cookie_authentication), prefix="/auth/cookie", tags=["auth"]
)
app.include_router(users.get_register_router(), prefix="/auth", tags=["auth"])
app.include_router(
    users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    users.get_verify_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(users.get_users_router(), prefix="/users", tags=["users"])


# Default endpoint
@app.get("/")
async def root():
    return {"message": "Hello!"}


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
