# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,Session
from pathlib import Path # Import Path

# Get the directory where this script (database.py) is located
BASE_DIR = Path(__file__).resolve().parent.parent

# Construct the absolute path to the database file in the project root
DATABASE_URL = f"sqlite:///{BASE_DIR / 'music_recommendation.db'}"

# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is needed for SQLite with FastAPI
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
def get_db():
    """
    Function to get the SessionLocal() object of the connections.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configure the sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Note: The Base is also imported and used in models.py
# The engine and SessionLocal are imported and used in routes and seed.py

