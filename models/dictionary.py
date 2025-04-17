from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mssql import NVARCHAR
from core.database import Base


class Dictionary(Base):
    """
    Represents a dictionary entry in the system, typically used for categories or types.

    Attributes:
        id (int): Unique identifier for the dictionary entry.
        name (str): The name of the dictionary entry (e.g., category name).

    Relationships:
        plans (Plans): The plans associated with this dictionary entry.
        payments (Payments): The payments associated with this dictionary entry.
    """

    __tablename__ = "dictionary"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(NVARCHAR(255), index=True)

    plans = relationship(
        "Plans", back_populates="dictionary", cascade="all, delete-orphan"
    )
    payments = relationship(
        "Payments", back_populates="dictionary", cascade="all, delete-orphan"
    )
