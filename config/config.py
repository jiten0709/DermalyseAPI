import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # PostgreSQL connection string
    username = os.getenv("POSTGRES_USERNAME")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    db = os.getenv("POSTGRES_DB")

    SQLALCHEMY_DATABASE_URI = f"postgresql://{username}:{password}@{host}:{port}/{db}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    