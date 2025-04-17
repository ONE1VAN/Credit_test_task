import pandas as pd
from sqlalchemy import create_engine
from core.database import SQLALCHEMY_DATABASE_URL

df = pd.read_csv("handlers/db_data/dictionary.csv", sep="\t")

if "id" in df.columns:
    df = df.drop(columns=["id"])

engine = create_engine(SQLALCHEMY_DATABASE_URL)

df.to_sql("dictionary", con=engine, index=False, if_exists="append")
