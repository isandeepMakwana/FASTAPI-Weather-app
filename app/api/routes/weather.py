from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import get_db
from app.models.weather import WeatherStats, WeatherRecords

router = APIRouter()

@router.get("/stats")
async def read_weather_stats(
    year_of_date: str = Query(None),
    id_of_station: str = Query(None),
    pagination: int = Query(1),
    size_of_query: int = Query(10),
    db: AsyncSession = Depends(get_db),
):
    """Endpoint for reading weather statistics"""
    try:
        query = select(WeatherStats)

        if year_of_date:
            query = query.where(WeatherStats.Date == year_of_date)
        if id_of_station:
            query = query.where(WeatherStats.Station_ID == id_of_station)

        offset_value = (pagination - 1) * size_of_query
        query = query.offset(offset_value).limit(size_of_query)
        
        result = await db.execute(query)
        weather_stats = result.scalars().all() 
        if not weather_stats:  # no data found
            raise HTTPException(status_code=200, detail="No data found for the specified dates/station id")

        return [
            {
                "id_of_station": stat.Station_ID, "date": stat.Date,"avg_max_temp": stat.AvgMaxTemp, "avg_min_temp": stat.AvgMinTemp,"total_acc_precipitation": stat.TotalAccPrecipitation,
            }
            for stat in weather_stats
        ]
    except Exception as e: # setup: no cover
        return {"message": e.detail}
    finally:    # close db connection
        await db.close()    

@router.get("/")
async def read_weather_records(
    date: str = Query(None),
    id_of_station: str = Query(None),
    pagination: int = Query(1),
    size_of_query: int = Query(10),
    db: AsyncSession = Depends(get_db),
):
    """Endpoint for reading weather records"""
    try:
        query = select(WeatherRecords)

        if date:
            query = query.where(WeatherRecords.Date == date)
        if id_of_station:
            query = query.where(WeatherRecords.Station_ID == id_of_station)

        offset_value = (pagination - 1) * size_of_query
        query = query.offset(offset_value).limit(size_of_query)
        
        result = await db.execute(query)
        weather_records = result.scalars().all() 

        if not weather_records:  # no data found
            raise HTTPException(status_code=404, detail="No data found for the specified date/station id")

        return [
            {
                "id_of_station": record.Station_ID,"date": record.Date,"max_temp": record.Max_Temp,"min_temp": record.Min_Temp,"precipitation": record.Precipitation,
            }
            for record in weather_records
        ]
    except Exception as e: # setup: no cover
        return {"message": e.detail}
    finally:    # close db connection 
        await db.close()