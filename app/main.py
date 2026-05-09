from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, documents, health
from app.core.config import get_settings
from app.core.container import ApplicationContainer
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.app_debug)


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = ApplicationContainer(settings)
    app.state.container = container
    yield
    container.close()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
