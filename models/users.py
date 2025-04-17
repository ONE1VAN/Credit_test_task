from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import relationship
from core.database import Base


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): Unique identifier for the user.
        login (str): The user's unique login.
        registration_date (date): The date when the user registered.

    Relationships:
        credits (Credits): The credits associated with the user.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255), unique=True, index=True)
    registration_date = Column(Date, index=True)

    credits = relationship(
        "Credits", back_populates="user", cascade="all, delete-orphan"
    )
