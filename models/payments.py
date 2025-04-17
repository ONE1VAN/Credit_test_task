from sqlalchemy import DECIMAL, Column, ForeignKey, Integer, Date
from sqlalchemy.orm import relationship
from core.database import Base


class Payments(Base):
    """
    Represents a payment made towards a credit, recording the amount, date, and type.

    Attributes:
        id (int): Unique identifier for the payment.
        credit_id (int): Foreign key linking the payment to a specific credit.
        payment_date (date): The date when the payment was made.
        type_id (int): Foreign key linking the payment to a specific type (e.g., body, interest) from the dictionary.
        sum (decimal): The amount of money paid.

    Relationships:
        credit (Credits): The credit associated with the payment.
        dictionary (Dictionary): The type of payment (e.g., body, interest) from the dictionary.
    """

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    credit_id = Column(Integer, ForeignKey("credits.id"))
    payment_date = Column(Date, index=True)
    type_id = Column(Integer, ForeignKey("dictionary.id"))
    sum = Column(DECIMAL(7, 2), index=True)

    credit = relationship("Credits", back_populates="payments")
    dictionary = relationship("Dictionary", back_populates="payments")
