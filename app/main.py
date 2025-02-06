from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes import weather, ingest
from app.services.ingest import data_ingestion
from app.core.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI): # setup: no cover
    data_ingestion('weather.db', settings.DATA_DIR)
    yield

app = FastAPI(lifespan=lifespan) 

# Include routers
app.include_router(weather.router, prefix="/api/weather", tags=["weather"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])