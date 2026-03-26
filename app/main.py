from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as user_router
from app.modules.assets.router import router as assets_router
from app.modules.watchlist.router import router as watchlist_router
from app.modules.watchlist.models import WatchlistItem
from app.modules.users.models import User
from app.modules.assets.models import Asset


import time
import logging
from fastapi import Request
from app.utils.logger import app_logger


app = FastAPI(title="CryptoDesk API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000" ,"http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(user_router ,prefix="/api/v1/users" , tags=["Users"])
app.include_router(assets_router, prefix="/api/v1/assets", tags=["Assets"])
app.include_router(watchlist_router, prefix="/api/v1/watchlist", tags=["Watchlist"])

@app.get("/health")
def health():
    return {"status": "ok"}



@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = round((time.time() - start_time) * 1000, 2)  # ms

    app_logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration,
        }
    )

    return response