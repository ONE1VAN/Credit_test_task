from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from core.database import Base


class Credits(Base):
    """
    Represents a credit record in the database.

    Attributes:
        id (int): Unique identifier for the credit.
        user_id (int): Foreign key linking to the user who owns the credit.
        issuance_date (date): The date the credit was issued.
        return_date (date): The date the credit is due to be returned.
        actual_return_date (date): The date the credit was actually returned.
        body (int): The principal amount of the credit.
        percent (decimal): The interest rate on the credit.

    Relationships:
        user (User): The user associated with the credit.
        payments (Payments): The payments made towards the credit.
    """

    __tablename__ = "credits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    issuance_date = Column(Date, index=True)
    return_date = Column(Date, index=True)
    actual_return_date = Column(Date, index=True)
    body = Column(Integer, index=True)
    percent = Column(DECIMAL(7, 1), index=True)

    user = relationship("User", back_populates="credits")
    payments = relationship(
        "Payments", back_populates="credit", cascade="all, delete-orphan"
    )
