# src/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite connection URL
SQLALCHEMY_DATABASE_URL = 'sqlite:///./energy.db'

# create_engine opens connection; for SQLite, disable same thread check
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}
)

# SessionLocal is used in service layer, not through router DI
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
