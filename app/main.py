from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.crud import post
from app.db.database import Base, engine # type: ignore
from app.api import auth # type: ignore
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from contextlib import asynccontextmanager
from app.routers.user import router as user_router # type: ignore
from app.models import follow, user # type: ignore
from app.routers import follow
from app.routers.post import router as post
from app.routers.comments import router as comments_router
from app.routers import like
from app.routers import feedexplore
from app.routers import notification
from app.routers.post import router as post_router
from app.routers import message
import logging
from fastapi.staticfiles import StaticFiles
from app.routers.search import router as search

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

# Lifespan context for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown logic (if any) goes here

# Create FastAPI app with lifespan handler
app = FastAPI(lifespan=lifespan)
#  Routers
app.include_router(auth.router)
app.include_router(user_router)
app.include_router(follow.router)
app.include_router(post)
app.include_router(comments_router)
app.include_router(like.router)
app.include_router(notification.router)
app.include_router(post_router)
app.include_router(notification.router) 
app.include_router(message.router)
app.include_router(feedexplore.router)
app.mount("/media", StaticFiles(directory="app/media"), name="media")
app.include_router(search, prefix="/api", tags=["Search"])
# Exception handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = [error['msg'] for error in exc.errors()]
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": error_messages[0]}
    )

