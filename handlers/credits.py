import pandas as pd
from sqlalchemy import create_engine
from core.database import SQLALCHEMY_DATABASE_URL

df = pd.read_csv(
    "handlers/db_data/credits.csv",
    sep="\t",
    parse_dates=["issuance_date", "return_date", "actual_return_date"],
    dayfirst=True,
    na_values=[""],
)


engine = create_engine(SQLALCHEMY_DATABASE_URL)

if "id" in df.columns:
    df = df.drop(columns=["id"])

date_columns = ["issuance_date", "return_date", "actual_return_date"]
for col in date_columns:
    df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce").dt.date

df.to_sql("credits", con=engine, if_exists="append", index=False)
