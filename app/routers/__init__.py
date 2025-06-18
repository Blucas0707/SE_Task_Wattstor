from .auth_router import router as auth_router
from .site_router import router as site_router
from .device_router import router as device_router
from .metric_router import router as metric_router
from .subscription_router import router as subscription_router

all_routers = [
    auth_router,
    site_router,
    device_router,
    metric_router,
    subscription_router,
]
