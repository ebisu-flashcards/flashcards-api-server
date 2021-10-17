from typing import List, Optional

from uuid import UUID
import databases
from sqlalchemy import Column, String, ForeignKey, Table, and_
from sqlalchemy.orm import Session
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from fastapi_users.models import UD

from flashcards_core.guid import GUID
from flashcards_core.database import init_db, Base, Deck
from flashcards_core.database.crud import CrudOperations
from flashcards_server.constants import (
    SQLALCHEMY_DATABASE_URL,
    SQLALCHEMY_DATABASE_CONNECTION_ARGS,
)
from flashcards_server.models import UserDB


#: Associative table for Decks and Users
DeckOwner = Table(
    "deck_owners",
    Base.metadata,
    Column("deck_id", GUID(), ForeignKey("decks.id"), primary_key=True),
    Column("owner_id", GUID(), ForeignKey("users.id"), nullable=False),
)


class User(Base, SQLAlchemyBaseUserTable, CrudOperations):

    #: The username
    username = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return (
            f"<User '{self.username}' (email: {self.email}, "
            f"{'enabled' if self.is_active else 'disabled'})>"
        )

    @classmethod
    def get_by_name(cls, session: Session, username: str):
        """
        Find a user by username. Usernames are unique.
        """
        return session.query(User).filter(User.username == username).first()

    @classmethod
    def get_by_email(cls, session: Session, email: str):
        """
        Find a user by email. Emails are unique.
        """
        return session.query(User).filter(User.email == email).first()

    def get_decks(
        self, session: Session, offset: int = 0, limit: int = 100
    ) -> List[Deck]:
        """
        Returns all the decks owned by this user.
        :param session: the session (see flashcards_core.database:init_session()).
        :param offset: for pagination, index at which to start returning values.
        :param limit: for pagination, maximum number of elements to return.
        :returns: List of Decks.
        """
        select = (
            DeckOwner.select()
            .where(DeckOwner.c.owner_id == self.id)
            .offset(offset)
            .limit(limit)
        )
        deck_owner_pairs = session.execute(select)
        return [
            Deck.get_one(session=session, object_id=pair.deck_id)
            for pair in deck_owner_pairs
        ]

    def owns_deck(self, session: Session, deck_id: UUID) -> bool:
        """
        Verify that the given deck is owned by this user.
        :param session: the session (see flashcards_core.database:init_session()).
        :param deck_id: the deck to check the ownership of.
        :returns: True if the user is the owner of this deck, False otherwise
        """
        select = DeckOwner.select().where(
            and_(DeckOwner.c.owner_id == self.id, DeckOwner.c.deck_id == deck_id)
        )
        deck_owner = session.execute(select)
        return len(list(deck_owner)) > 0

    def create_deck(self, session: Session, deck_data: dict):
        """
        Create a new deck and assign it to this user.
        :param deck_data: the data of the deck to create.
        :param session: the session (see flashcards_core.database:init_db()).
        """
        new_deck = Deck.create(session=session, **deck_data)
        insert = DeckOwner.insert().values(owner_id=self.id, deck_id=new_deck.id)
        session.execute(insert)
        session.commit()
        session.refresh(self)
        return new_deck

    def delete_deck(self, session: Session, deck_id: UUID) -> None:
        """
        Remove the given deck from this user and delete it.
        :param deck_id: the ID of the deck to remove.
        :param session: the session (see flashcards_core.database:init_db()).
        :returns: None.
        """
        Deck.delete(session=session, object_id=deck_id)
        delete = DeckOwner.delete().where(DeckOwner.c.deck_id == deck_id)
        session.execute(delete)
        session.commit()
        session.refresh(self)


session_local = init_db(SQLALCHEMY_DATABASE_URL, SQLALCHEMY_DATABASE_CONNECTION_ARGS)
database = databases.Database(SQLALCHEMY_DATABASE_URL)
user_db = SQLAlchemyUserDatabase(UserDB, database, User.__table__)


async def get_by_email_or_username(self, email: str) -> Optional[UD]:
    query_email = self.users.select().where(self.users.c.email == email)
    user_email = await self.database.fetch_one(query_email)

    query_name = self.users.select().where(self.users.c.username == email)
    user_name = await self.database.fetch_one(query_name)

    if user_email:
        return await self._make_user(user_email)
    if user_name:
        return await self._make_user(user_name)
    return None


user_db.get_by_email = get_by_email_or_username.__get__(user_db)


def get_user_db():
    yield user_db


def get_session() -> Session:
    """
    Allows other parts of the app to access the database properly
    FastAPI "Dependency" (used with Depends)
    """
    session = session_local()
    try:
        yield session
    finally:
        session.close()
