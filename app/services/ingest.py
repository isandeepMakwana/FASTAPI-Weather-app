
from app.core.database import Base
from app.core.settings import settings
import dask.dataframe as daskDataFrame
import os
import logging
from sqlalchemy import create_engine
import datetime

logging.basicConfig(
    filename='data_ingestion.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def create_engine_and_tables(database_name):
    engine = create_engine(f'sqlite:///{database_name}', echo=True)
    Base.metadata.create_all(bind=engine)
    return engine

def read_data(filepath):
    """Reading Data through txt files"""
    data = daskDataFrame.read_csv(filepath, sep="\t", header=None,
                                  names=["date", "max_temp", "min_temp", "precipitation"])
    data["Station_ID"] = os.path.basename(filepath)[:11]
    return data

def clean_data(data):
    result = data[(data['max_temp'] != -9999) |
                  (data['min_temp'] != -9999) | (data['precipitation'] != -9999)]

    result = result.groupby(['Station_ID', data['date'].map(str).str[:4]]).agg({
        'max_temp': 'mean',
        'min_temp': 'mean',
        'precipitation': 'sum'
    }).reset_index()

    heading = {'max_temp': 'AvgMaxtemp', 'min_temp': 'AvgMintemp',
               'precipitation': 'TotalAccPrecipitation'}
    result.rename(columns=heading, inplace=True)
    return result

def write_to_database(engine, data, result):
    """Ingesting the data from txt to database"""
    start_time = datetime.datetime.now()
    logging.info(f"start time of ingestion {start_time}")
    session = engine.raw_connection()
    data.to_sql("weather_records", session, if_exists="replace",
                    index=True, index_label='id')
    result.to_sql("weather_stats", session, if_exists="replace",
                      index=True, index_label='id')
    session.commit()
    end_time = datetime.datetime.now()
    logging.info(f"End time of ingestion {end_time}")
    time_taken = end_time - start_time

    logging.info(f"Time taken: {time_taken.total_seconds():.2f} seconds")


def data_ingestion(database_name, directory):
    engine = create_engine_and_tables(database_name)
    dataframes = []
    for file_data in os.listdir(directory):
        if file_data.endswith(".txt"):
            filepath = os.path.join(directory, file_data)
            data = read_data(filepath)
            dataframes.append(data)
    data = daskDataFrame.concat(dataframes).compute().reset_index(drop=True)
    result = clean_data(data)
    write_to_database(engine, data, result)
