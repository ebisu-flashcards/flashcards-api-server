from typing import List

from uuid import uuid4, UUID
from sqlalchemy import Column, String, Boolean, ForeignKey, Table, and_
from sqlalchemy.orm import Session
from flashcards_core.guid import GUID
from flashcards_core.database import Base, Deck
from flashcards_core.database.crud import CrudOperations


#: Associative table for Decks and Users
DeckOwner = Table(
    "deck_owners",
    Base.metadata,
    Column("deck_id", GUID(), ForeignKey("decks.id"), primary_key=True),
    Column("owner_id", GUID(), ForeignKey("users.id"), nullable=False),
)


class User(Base, CrudOperations):
    __tablename__ = "users"

    #: Primary key
    id = Column(GUID(), primary_key=True, index=True, default=uuid4)

    #: The username
    username = Column(String, unique=True, nullable=False)

    #: The email
    email = Column(String, unique=True, nullable=False)

    #: The hash of the password
    hashed_password = Column(String, nullable=False)

    #: If the user is disabled or not
    disabled = Column(Boolean, nullable=False, default=False)

    def __repr__(self):
        return (
            f"<User '{self.username}' "
            f"({'disabled' if self.disabled else 'active'}, "
            f"ID: {self.id})>"
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
