from fastapi import FastAPI

from contextlib import asynccontextmanager
from app.config.server import Server
from app.config.settings import SETTINGS
from app.config.database import database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("App is starting...")
    
    server = Server(app)
    server.start()
    
    # Application running
    yield
    
    # Shutdown logic
    print("App is shutting down...")
    
    
    server.stop()


# FastAPI app with custom configuration for Swagger
app = FastAPI(
    title=SETTINGS.app_name,
    description=SETTINGS.app_description,
    version=SETTINGS.app_version,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    lifespan=lifespan,  # Custom lifespan for startup/shutdown events
)

