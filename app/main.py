from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.db_session import get_db
from app.core.database import Base, engine
from app.mock_data import init_mock_data
from app.routers import all_routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    db = next(get_db())
    init_mock_data(db)
    yield


app = FastAPI(title='Energy Management API', lifespan=lifespan)

# Include routers
for router in all_routers:
    app.include_router(router)
