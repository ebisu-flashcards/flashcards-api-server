from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import CookieAuthentication
from fastapi_users.db import SQLAlchemyUserDatabase

from flashcards_server.database import get_user_db
from flashcards_server.models import User, UserCreate, UserDB, UserUpdate
from flashcards_server.constants import SECRET_KEY


class UserManager(BaseUserManager[UserCreate, UserDB]):
    user_db_model = UserDB
    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY

    async def on_after_register(self, user: UserDB, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserDB, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


cookie_authentication = CookieAuthentication(
    cookie_name="flashcards", secret=SECRET_KEY, lifetime_seconds=3600
)

users = FastAPIUsers(
    get_user_manager,
    [cookie_authentication],
    User,
    UserCreate,
    UserUpdate,
    UserDB,
)

current_active_user = users.current_user(active=True)
