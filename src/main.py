from logging import getLogger

from api import file_router, router_healthcheck, user_router
from utils.helpers import configure_app

logger = getLogger("main")
app = configure_app()

app.include_router(router_healthcheck, tags=["healthcheck"], prefix="/ping")
app.include_router(file_router, tags=["files"], prefix="/files")
app.include_router(user_router, tags=["users"])
