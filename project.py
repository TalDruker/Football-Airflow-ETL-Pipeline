from airflow.decorators import dag, task
from datetime import datetime, timedelta
import pandas as pd
import logging
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mongo.hooks.mongo import MongoHook

# Initialize logger for task execution tracking
logger = logging.getLogger("airflow.task")



# Default DAG configuration parameters
default_args = {
    'owner': 'Tal',
    'retries': 3,
    'retry_delay': timedelta(minutes=2)
}

@dag(
    dag_id='project_v1',
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule='@daily',
    tags=['football'],
    catchup=False
)
def project():


    """
    Automated Football Data ETL Pipeline:
    1. Extract: Ingests raw match records from MongoDB.
    2. Transform: Sanitizes, normalizes, and cleans player metrics using Pandas.
    3. Load: Persists structured dataset into target PostgreSQL database.
    """
   
    @task
  
       # Extracts raw documents from MongoDB collection and drops internal identifiers.
      
    def extract_data_from_mongo():
        try:
            hook = MongoHook(mongo_conn_id='mongo_conn')
            collection = hook.get_collection('football', mongo_db='projectPac')
            data = list(collection.find())

            if not data:
                raise ValueError("No data found in MongoDB collection 'football'")

            df = pd.DataFrame(data)
            if '_id' in df.columns:
                df = df.drop(columns=['_id'])

            logger.info(f"Successfully extracted {len(df)} rows")
            return df
        except Exception as e:
            logger.error(f"Extraction error: {str(e)}")
            raise e

    @task

    
    def transform_data(df):
        """
        Cleans and normalizes football performance dataset:
        - Handles missing values and invalid date formats.
        - Caps metric outliers (Distance, Yellow/Red cards, Age).
        - Standardizes position aliases and fixes string encoding issues.
        """
        try:
            df['Match_Date'] = pd.to_datetime(df['Match_Date'], errors='coerce')
            df['Distance_KM'] = df['Distance_KM'].fillna(7.8)
            df['Match_Date']=df['Match_Date'].fillna('23/01/2024')
            df.loc[df['Distance_KM'] > 14, 'Distance_KM'] = 12
            df.loc[df['Yellow_Cards'] > 2, 'Yellow_Cards'] = 2
            df.loc[df['Red_Cards'] > 1, 'Red_Cards'] = 1
            df.loc[df['Yellow_Cards'] == 2, 'Red_Cards'] = 1
            df.loc[df['Position'] == 'קשר', 'Position'] = 'Midfielder'
            df.loc[df['Position'].isin(['FWD', 'חלוץ']) , 'Position'] = 'Forward'
            df.loc[df['Minutes_Played'] == 0, 'Minutes_Played'] = 74
            df['Assists'] = df['Assists'].abs()
            df['Goals'] = df['Goals'].abs()
            df.loc[df['Age'] < 16, 'Age'] = 16
            df.loc[df['Age'] > 40, 'Age'] = 40
            df['Team'] = df['Team'].str.title().str.strip().replace('Beitar Jeru', 'Beitar Jerusalem')

            return df
        except Exception as e:
            logger.error(f"Transformation error: {str(e)}")
            raise e

    @task
    def load_data_to_postgres(df):
       """
        Loads cleaned DataFrame into target PostgreSQL relational table.
        """
       try:
           pg_hook = PostgresHook(postgres_conn_id='postgre_conn') 
           engine = pg_hook.get_sqlalchemy_engine()
        
           logger.info(f"Engine URL: {engine.url}")
           logger.info(f"Loading {len(df)} rows to PostgreSQL")
        

        # Overwrite target table 'football' with processed batch
           df.to_sql('football', engine, if_exists='replace', index=False)
           logger.info("Successfully loaded data to PostgreSQL")
            
       except Exception as e:
        logger.error(f"Load error: {str(e)}")
        raise e

       
# ETL Dependency Flow Definition
    df = extract_data_from_mongo()
    transformed_df = transform_data(df)
    load_data_to_postgres(transformed_df)


# Instantiate DAG
project()