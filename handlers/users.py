import pandas as pd
from sqlalchemy import create_engine
from core.database import SQLALCHEMY_DATABASE_URL

df = pd.read_csv("handlers/db_data/users.csv", sep="\t")


engine = create_engine(SQLALCHEMY_DATABASE_URL)

if "id" in df.columns:
    df = df.drop(columns=["id"])
df["registration_date"] = pd.to_datetime(df["registration_date"], dayfirst=True)
df.to_sql("users", con=engine, if_exists="append", index=False)
