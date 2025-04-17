import pandas as pd
from sqlalchemy import create_engine
from core.database import SQLALCHEMY_DATABASE_URL

df = pd.read_csv("handlers/db_data/plans.csv", sep="\t")


engine = create_engine(SQLALCHEMY_DATABASE_URL)

if "id" in df.columns:
    df = df.drop(columns=["id"])
df["period"] = pd.to_datetime(df["period"], dayfirst=True)
df.to_sql("plans", con=engine, if_exists="append", index=False)
