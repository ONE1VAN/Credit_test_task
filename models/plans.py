from sqlalchemy import Column, ForeignKey, Integer, Date
from sqlalchemy.orm import relationship
from core.database import Base


class Plans(Base):
    """
    Represents a financial plan associated with a specific period and category.

    Attributes:
        id (int): Unique identifier for the plan.
        period (date): The date representing the period for the plan (e.g., the first day of the month).
        sum (int): The monetary value of the plan (e.g., the planned amount for the period).
        category_id (int): The foreign key linking the plan to a specific category in the dictionary.

    Relationships:
        dictionary (Dictionary): The dictionary entry associated with the plan's category.
    """

    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    period = Column(Date, index=True)
    sum = Column(Integer, index=True)
    category_id = Column(Integer, ForeignKey("dictionary.id"))

    dictionary = relationship("Dictionary", back_populates="plans")
