from typing import AsyncGenerator, List

from uuid import UUID

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Table, and_
from sqlalchemy.orm import Session


from flashcards_core.guid import GUID
from flashcards_core.database import Base, Deck, Card, Tag, Fact, Review


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    
    @classmethod
    async def get_by_name(cls, session: Session, username: str) -> 'User':
        """
        Find a user by username. Usernames are unique.
        """
        return session.query(cls).filter(cls.username == username).first()

    @classmethod
    async def get_by_email(cls, session: Session, email: str) -> 'User':
        """
        Find a user by email. Emails are unique.
        """
        return session.query(cls).filter(cls.email == email).first()

    async def get_decks(
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
        deck_owner_pairs = await session.execute(select)
        return list([
            await Deck.get_one_async(session=session, object_id=pair.deck_id)
            for pair in deck_owner_pairs
        ])

    async def owns_deck(self, session: Session, deck_id: UUID) -> bool:
        """
        Verify that the given deck is owned by this user.
        :param session: the session (see flashcards_core.database:init_session()).
        :param deck_id: the deck to check the ownership of.
        :returns: True if the user is the owner of this deck, False otherwise
        """
        select = DeckOwner.select().where(
            and_(DeckOwner.c.owner_id == self.id, DeckOwner.c.deck_id == deck_id)
        )
        deck_owner = await session.execute(select)
        return len(list(deck_owner)) > 0

    async def create_deck(self, session: Session, deck_data: dict) -> Deck:
        """
        Create a new deck and assign it to this user.
        :param deck_data: the data of the deck to create.
        :param session: the session (see flashcards_core.database:init_db()).
        """
        new_deck = await Deck.create_async(session=session, **deck_data)
        insert = DeckOwner.insert().values(owner_id=self.id, deck_id=new_deck.id)
        await session.execute(insert)
        await session.commit()
        return new_deck

    async def delete_deck(self, session: Session, deck_id: UUID) -> None:
        """
        Remove the given deck from this user and delete it.
        :param deck_id: the ID of the deck to remove.
        :param session: the session (see flashcards_core.database:init_db()).
        :returns: None.
        """
        Deck.delete_async(session=session, object_id=deck_id)
        delete = DeckOwner.delete().where(DeckOwner.c.deck_id == deck_id)
        session.execute(delete)
        session.commit()
        session.refresh(self)



#: Associative table for Decks and Users
DeckOwner = Table(
    "deck_owners",
    Base.metadata,
    Column("deck_id", GUID(), ForeignKey(Deck.id), primary_key=True),
    Column("owner_id", GUID(), ForeignKey(User.id), nullable=False),
)



DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
