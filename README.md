# FastAPI Credit Management Service

A backend service built with **FastAPI**, **SQLAlchemy**, and **MSSQL** for managing **user credits**, **payment plans**, and **payments**.  
The project also supports **CSV data import** into the database.

---


## 🛠️ Setup Instructions

**Install dependencies**:

   pip install -r requirements.txt
   
Configure environment variables:
Copy .env from the provided example:

cp example.env .env


# Run the FastAPI application:


uvicorn main:app --reload

# 📥 Import CSV Data to Database
To load data from .csv files located in the db_data/ directory into the database, run the corresponding handler script:

python -m handlers.credits

python -m handlers.users

python -m handlers.plans

python -m handlers.payments

python -m handlers.dictionary

Each command will parse the CSV file and insert data into the corresponding database table using SQLAlchemy.
