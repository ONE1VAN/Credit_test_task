from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    DB_DRIVER: str = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_SERVER: str = os.getenv("DB_SERVER", "127.0.0.1")
    DB_NAME: str = os.getenv("DB_NAME", "credits_fastapi")
    DB_USER: str = os.getenv("DB_USER", "sa")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "securepassword1234")


settings = Settings()
