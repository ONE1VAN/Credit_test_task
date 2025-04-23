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
from datetime import date
from db_operations.crud import (
    get_credits_by_user_id,
    get_total_payments,
    get_total_payment_by_type,
    calculate_overdue_days,
    get_existing_plan,
    create_plan,
    count_issuances_in_month,
    get_plan_sum_issuance,
    get_issuances_for_month,
    count_payments_in_month,
    get_plan_sum_for_payments,
    get_sum_payments_for_month,
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


@app.get("/year_performance")
def year_performance(year: int, db: Session = Depends(get_db)):
    """
    Retrieves a year’s performance data, including monthly and total issuance and payment performance.

    Returns:
    - Monthly data: Issuances, payments, and plan performance (in %).
    - Total data: Aggregated performance for the year (total issuances, payments, and performance percentages).

    The performance is calculated as the ratio of actual values to planned values, presented as a percentage.
    """
    current_date = date.today()
    current_year = current_date.year
    if year < 2000 or year > current_year + 1:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid year: {year}. Must be between 2000 and {current_year + 1}.",
        )

    results = []
    for month in range(1, 13):
        issuances = count_issuances_in_month(db, year, month)
        plan_sum_issuances = get_plan_sum_issuance(db, year, month)
        sum_issuances_for_month = get_issuances_for_month(db, year, month)
        issuance_plan_percent = round(
            (
                (sum_issuances_for_month / plan_sum_issuances * 100)
                if plan_sum_issuances
                else 0
            ),
            2,
        )
        payments_in_month = count_payments_in_month(db, year, month)
        plan_sum_for_payments = get_plan_sum_for_payments(db, year, month)
        sum_payments_for_month = get_sum_payments_for_month(db, year, month)
        payment_plan_performance_percent = round(
            (
                (sum_payments_for_month / plan_sum_for_payments * 100)
                if plan_sum_for_payments
                else 0
            ),
            2,
        )

        results.append(
            {
                "month": month,
                "year": year,
                "issuances": issuances,
                "plan_sum_issuances": plan_sum_issuances,
                "sum_issuances_for_month": sum_issuances_for_month,
                "issuance_plan_percent": f"{issuance_plan_percent}%",
                "payments_in_month": payments_in_month,
                "plan_sum_for_payments": plan_sum_for_payments,
                "sum_payments_for_month": sum_payments_for_month,
                "payment_plan_performance_percent": f"{payment_plan_performance_percent}%",
            }
        )

    total_sum_issuances = sum(item["sum_issuances_for_month"] for item in results)
    plan_sum_issuances = sum(item["plan_sum_issuances"] for item in results)
    total_plan_sum_for_payments = sum(item["plan_sum_for_payments"] for item in results)
    total_sum_payments_for_month = sum(
        item["sum_payments_for_month"] for item in results
    )

    for item in results:
        item["sum_month_issuance_percent"] = (
            f"{round((item['sum_issuances_for_month'] / total_sum_issuances * 100) if total_sum_issuances else 0, 2)}%"
        )
        item["sum_month_payment_percent"] = (
            f"{round((item['sum_payments_for_month'] / total_sum_payments_for_month * 100) if total_sum_payments_for_month else 0, 2)}%"
        )

    results.append(
        {
            "total_issuances": sum(item["issuances"] for item in results),
            "year": year,
            "plan_sum_issuances": plan_sum_issuances,
            "total_sum_issuances_for_month": total_sum_issuances,
            "total_issuance_plan_percent": f"{round((total_sum_issuances / plan_sum_issuances * 100) if plan_sum_issuances else 0, 2)}%",
            "total_payments_in_month": sum(
                item["payments_in_month"] for item in results
            ),
            "total_plan_sum_for_payments": total_plan_sum_for_payments,
            "total_sum_payments_for_month": total_sum_payments_for_month,
            "total_payment_plan_performance_percent": f"{round((total_sum_payments_for_month / total_plan_sum_for_payments * 100) if total_plan_sum_for_payments else 0, 2)}%",
        }
    )

    return results
