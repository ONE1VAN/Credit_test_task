from models.users import User
from models.credits import Credits
from models.payments import Payments
from models.dictionary import Dictionary
from models.plans import Plans
from core.database import SessionLocal, engine
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from core.database import Base
from fastapi import UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
import io
from db_operations.crud import (
    get_credits_by_user_id,
    get_total_payments,
    get_total_payment_by_type,
    calculate_overdue_days,
    get_existing_plan,
    create_plan,
)

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    """
    Dependency that provides a database session and ensures it is closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/user_credits/{user_id}")
def get_user_credits(user_id: int, db: Session = Depends(get_db)):
    """
    Returns a list of credit details for a given user.

    Each credit includes:
    - issuance date
    - whether the credit is closed
    - for closed credits: actual return date, body, percent, total payments
    - for open credits: planned return date, overdue days, body, percent,
      payments by body and percent

    Raises:
        HTTPException: If no credits are found for the user.
    """
    credits = get_credits_by_user_id(db, user_id)

    if not credits:
        raise HTTPException(status_code=404, detail="User or credits not found")

    result = []
    for credit in credits:
        is_closed = credit.actual_return_date is not None
        credit_data = {"issuance_date": credit.issuance_date, "is_closed": is_closed}

        if is_closed:
            credit_data.update(
                {
                    "actual_return_date": credit.actual_return_date,
                    "body": credit.body,
                    "percent": credit.percent,
                    "total_payments": get_total_payments(db, credit.id),
                }
            )
        else:
            credit_data.update(
                {
                    "return_date": credit.return_date,
                    "overdue_days": calculate_overdue_days(credit.return_date),
                    "body": credit.body,
                    "percent": credit.percent,
                    "body_payments": get_total_payment_by_type(db, credit.id, "body"),
                    "percent_payments": get_total_payment_by_type(
                        db, credit.id, "percent"
                    ),
                }
            )

        result.append(credit_data)

    return result


@app.post("/plans_insert")
def plans_insert(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Uploads a monthly plans file and inserts valid entries into the database.

    The file must be in Excel (.xlsx/.xls) or tab-separated CSV format, and contain
    the columns: 'period', 'sum', and 'category_id'.

    Validations:
    - 'period' must be the first day of the month.
    - 'sum' must not be empty (0 is allowed).
    - A plan with the same 'period' and 'category_id' must not already exist.

    Raises:
        HTTPException: On invalid file format, missing/invalid fields, or duplicates.
    """
    try:
        if file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
            df = pd.read_excel(file.file)
        else:
            contents = file.file.read()
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")), sep="\t")
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Please upload an Excel or tab-separated CSV file.",
        )

    df.columns = df.columns.str.strip().str.lower()

    required_columns = {"period", "sum", "category_id"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail=f"The file must contain the following columns: {required_columns}",
        )

    for index, row in df.iterrows():
        try:
            period = pd.to_datetime(row["period"], dayfirst=True).date()
        except Exception:
            raise HTTPException(
                status_code=400, detail=f"Invalid date format in row {index + 1}"
            )

        if period.day != 1:
            raise HTTPException(
                status_code=400,
                detail=f"Date in row {index + 1} must be the first day of the month",
            )

        if pd.isnull(row["sum"]):
            raise HTTPException(
                status_code=400, detail=f"The 'sum' field in row {index + 1} is empty"
            )

        try:
            category_id = int(row["category_id"])
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Invalid category_id in row {index + 1}"
            )

        if get_existing_plan(db, period, category_id):
            raise HTTPException(
                status_code=400,
                detail=f"A plan for period {period} and category {category_id} already exists (row {index + 1})",
            )

        create_plan(db, period, int(row["sum"]), category_id)

    db.commit()
    return JSONResponse(
        content={"message": "Plans were successfully inserted into the database."}
    )
