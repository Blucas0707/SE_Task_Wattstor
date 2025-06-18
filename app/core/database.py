from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from settings import DATABASE_URL

print(f'{DATABASE_URL=}')

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

# SessionLocal is used in service layer, not through router DI
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
