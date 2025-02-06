
import asyncio
from app.services.ingest import data_ingestion
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def ingest_weather_records():
    """Endpoint for ingest weather records"""
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, data_ingestion, 'weather.db', './wx_data')
    except Exception as e: # setup: no cover
        return {"message": f"An Error Occurred {e}"}
    return {"message": "Data successfully ingested in DB"}