# src/main.py
from fastapi import FastAPI
from app.core.database import Base, engine
# from .routers import site_router, device_router, metric_router, subscription_router
from app.routers import site_router, device_router, metric_router, subscription_router, auth_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Energy Management API")

# Include routers
app.include_router(auth_router.router)
app.include_router(site_router.router)
app.include_router(device_router.router)
app.include_router(metric_router.router)
app.include_router(subscription_router.router)
