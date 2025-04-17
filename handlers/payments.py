import pandas as pd
from sqlalchemy import create_engine
from core.database import SQLALCHEMY_DATABASE_URL

df = pd.read_csv("handlers/db_data/payments.csv", sep="\t")


engine = create_engine(SQLALCHEMY_DATABASE_URL)

if "id" in df.columns:
    df = df.drop(columns=["id"])
df["payment_date"] = pd.to_datetime(df["payment_date"], dayfirst=True)
df.to_sql("payments", con=engine, if_exists="append", index=False)
