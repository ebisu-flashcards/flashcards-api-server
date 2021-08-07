from uuid import uuid4
from sqlalchemy import Column, String, Boolean

from flashcards_core.guid import GUID
from flashcards_core.database import Base
from flashcards_core.database.crud import CrudOperations


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
    disabled = Column(Boolean, nullable=False)

    def __repr__(self):
        return (
            f"<User '{self.username}' "
            f"({'disabled' if self.disabled else 'active'}, "
            f"ID: {self.id})>"
        )
