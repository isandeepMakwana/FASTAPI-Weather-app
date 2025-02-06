from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base

class WeatherStats(Base):
    __tablename__ = "weather_stats"
    id = Column(Integer, primary_key=True, index=True)
    Station_ID = Column(String, index=True)
    Date = Column(String, index=True)
    AvgMaxTemp = Column(Float)
    AvgMinTemp = Column(Float)
    TotalAccPrecipitation = Column(Float)

class WeatherRecords(Base):
    __tablename__ = "weather_records"
    id = Column(Integer, primary_key=True, index=True)
    Date = Column(String, index=True)
    Max_Temp = Column(Float)
    Min_Temp = Column(Float)
    Precipitation = Column(Float)
    Station_ID = Column(String, index=True)