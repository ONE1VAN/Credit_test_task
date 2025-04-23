from sqlalchemy.orm import Session
from sqlalchemy import func
from models.payments import Payments
from models.dictionary import Dictionary
from models.credits import Credits
from datetime import date
from models.plans import Plans
from sqlalchemy import extract


def get_credits_by_user_id(db: Session, user_id: int):
    """
    Retrieves all credits associated with a specific user by their user ID.

    Args:
        db (Session): The database session to execute the query.
        user_id (int): The ID of the user whose credits are to be retrieved.

    Returns:
        list: A list of `Credit` objects associated with the specified user.

    Raises:
        None: If no credits are found, an empty list is returned.
    """
    return db.query(Credits).filter(Credits.user_id == user_id).all()


def get_total_payment_by_type(db: Session, credit_id: int, type_name: str) -> float:
    """
    Retrieves the total payment amount for a specific credit and payment type.

    Args:
        db (Session): The database session to execute the query.
        credit_id (int): The ID of the credit for which the total payment is calculated.
        type_name (str): The name of the payment type (e.g., "body" or "percent").

    Returns:
        float: The total sum of payments for the specified credit and payment type.
              Returns 0 if no payments are found or if the type name is invalid.

    Raises:
        None: If the payment type name is invalid or no payments are found, 0 is returned.
    """
    type_id = db.query(Dictionary.id).filter(Dictionary.name == type_name).first()
    if not type_id:
        return 0
    total = (
        db.query(func.sum(Payments.sum))
        .filter(Payments.credit_id == credit_id, Payments.type_id == type_id[0])
        .scalar()
    )
    return total or 0


def get_total_payments(db: Session, credit_id: int) -> float:
    """
    Retrieves the total payment amount for a specific credit.

    Args:
        db (Session): The database session to execute the query.
        credit_id (int): The ID of the credit for which the total payment is calculated.

    Returns:
        float: The total sum of payments for the specified credit.
              Returns 0 if no payments are found.

    Raises:
        None: If no payments are found for the given credit, 0 is returned.
    """
    return (
        db.query(func.sum(Payments.sum))
        .filter(Payments.credit_id == credit_id)
        .scalar()
        or 0
    )


def calculate_overdue_days(return_date: date) -> int:
    """
    Calculates the number of overdue days for a credit based on its return date.

    Args:
        return_date (date): The return date of the credit.

    Returns:
        int: The number of overdue days. Returns 0 if the return date is not overdue.

    Raises:
        None: If the return date is in the future, returns 0 as there are no overdue days.
    """
    overdue = (date.today() - return_date).days
    return max(overdue, 0)


def get_existing_plan(db: Session, period: date, category_id: int) -> Plans | None:
    """
    Checks if a plan exists in the database for a specific period and category.

    Args:
        db (Session): The database session.
        period (date): The period for which the plan is being checked.
        category_id (int): The ID of the category for which the plan is being checked.

    Returns:
        Plans | None: The existing plan if found, otherwise None.
    """
    return db.query(Plans).filter_by(period=period, category_id=category_id).first()


def create_plan(db: Session, period: date, sum_: int, category_id: int) -> Plans:
    """
    Creates a new plan and adds it to the database.

    Args:
        db (Session): The database session.
        period (date): The period for the new plan.
        sum_ (int): The amount of the new plan.
        category_id (int): The ID of the category for the new plan.

    Returns:
        Plans: The newly created plan.
    """
    new_plan = Plans(period=period, sum=sum_, category_id=category_id)
    db.add(new_plan)
    return new_plan


def count_issuances_in_month(db: Session, year: int, month: int):
    """
    Counts the number of credit issuances in a specific month and year.

    Args:
        db (Session): The database session.
        year (int): The year for which the issuances are being counted.
        month (int): The month for which the issuances are being counted.

    Returns:
        int: The number of issuances in the specified month and year.
    """
    return (
        db.query(Credits)
        .filter(
            extract("year", Credits.issuance_date) == year,
            extract("month", Credits.issuance_date) == month,
        )
        .count()
    )


def get_plan_sum_issuance(db: Session, year: int, month: int):
    """
    Retrieves the total sum of the issuance plan for a specific month and year.

    Args:
        db (Session): The database session.
        year (int): The year for which the plan sum is being calculated.
        month (int): The month for which the plan sum is being calculated.

    Returns:
        float: The total sum of the issuance plan for the specified month and year.
              Returns 0 if no plan sum is found.
    """
    return (
        db.query(Plans)
        .join(Dictionary)
        .filter(
            extract("year", Plans.period) == year,
            extract("month", Plans.period) == month,
            Dictionary.name == "issuance",
        )
        .with_entities(func.sum(Plans.sum))
        .scalar()
        or 0
    )


def get_issuances_for_month(db: Session, year: int, month: int):
    """
    Retrieves the total sum of issuances for a specific month and year.

    Args:
        db (Session): The database session.
        year (int): The year for which the issuances are being calculated.
        month (int): The month for which the issuances are being calculated.

    Returns:
        float: The total sum of the issuances for the specified month and year.
              Returns 0 if no issuances are found.
    """
    return (
        db.query(func.sum(Credits.body))
        .filter(
            extract("year", Credits.issuance_date) == year,
            extract("month", Credits.issuance_date) == month,
        )
        .scalar()
        or 0
    )


def count_payments_in_month(db: Session, year: int, month: int):
    """
    Counts the number of payments in a specific month and year.

    Args:
        db (Session): The database session.
        year (int): The year for which the payments are being counted.
        month (int): The month for which the payments are being counted.

    Returns:
        int: The number of payments in the specified month and year.
    """
    return (
        db.query(Payments)
        .join(Credits)
        .filter(
            extract("year", Payments.payment_date) == year,
            extract("month", Payments.payment_date) == month,
        )
        .count()
    )


def get_plan_sum_for_payments(db: Session, year: int, month: int):
    """
    Retrieves the total sum of the payment plan for a specific month and year.

    Args:
        db (Session): The database session.
        year (int): The year for which the payment plan sum is being calculated.
        month (int): The month for which the payment plan sum is being calculated.

    Returns:
        int: The total sum of the payment plan for the specified month and year.
              Returns 0 if no plan sum is found.
    """
    return (
        db.query(Plans)
        .join(Dictionary)
        .filter(
            extract("year", Plans.period) == year,
            extract("month", Plans.period) == month,
            Dictionary.name == "collection",
        )
        .with_entities(func.sum(Plans.sum))
        .scalar()
        or 0
    )


def get_sum_payments_for_month(db: Session, year: int, month: int):
    """
    Retrieves the total sum of payments for a specific month and year.

    Args:
        db (Session): The database session.
        year (int): The year for which the payments are being calculated.
        month (int): The month for which the payments are being calculated.

    Returns:
        float: The total sum of payments for the specified month and year.
              Returns 0 if no payments are found.
    """
    return (
        db.query(func.sum(Payments.sum))
        .join(Credits)
        .filter(
            extract("year", Payments.payment_date) == year,
            extract("month", Payments.payment_date) == month,
        )
        .scalar()
        or 0
    )
