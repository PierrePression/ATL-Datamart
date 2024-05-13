import gc
import http
import os
import sys

import pandas as pd
from minio import Minio
from sqlalchemy import create_engine
from io import BytesIO


def get_db_config():
    db_config = {
        "dbms_engine": "postgresql",
        "dbms_username": "postgres",
        "dbms_password": "admin",
        "dbms_ip": "localhost",
        "dbms_port": "15432",
        "dbms_database": "nyc_warehouse",
        "dbms_table": "nyc_raw"
    }

    db_config["database_url"] = (
        f"{db_config['dbms_engine']}://{db_config['dbms_username']}:{db_config['dbms_password']}@"
        f"{db_config['dbms_ip']}:{db_config['dbms_port']}/{db_config['dbms_database']}"
    )
    return db_config

def get_minio_client():
    return Minio(
        "localhost:9000",
        secure=False,
        access_key="minio",
        secret_key="minio123"
    )

def write_data_postgres(dataframe: pd.DataFrame, db_config) -> bool:
    try:
        engine = create_engine(db_config["database_url"])
        with engine.connect():
            success: bool = True
            print("Connection successful! Processing parquet file")
            dataframe.to_sql(db_config["dbms_table"], engine, index=True, if_exists='append', chunksize=500)

    except Exception as e:
        success: bool = False
        print(f"Error connection to the database: {e}")
        return success

    return success

def clean_column_name(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe.columns = map(str.lower, dataframe.columns)
    return dataframe

def process_parquet_file(client, bucket, parquet_file, db_config):
    try:
        response = client.get_object(bucket, parquet_file.object_name)
        parquet_df = pd.read_parquet(BytesIO(response.data), engine='pyarrow')
        clean_column_name(parquet_df)
        if not write_data_postgres(parquet_df, db_config):
            del parquet_df
            gc.collect()
            return False
        del parquet_df
        gc.collect()
        return True
    except Exception as e:
        print(f"Error processing parquet file: {e}")
        return False

def main() -> None:
    client = get_minio_client()
    bucket: str = "taxi"
    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket)
    else:
        print(f"Bucket {bucket} already exists")

    db_config = get_db_config()

    parquet_files = client.list_objects(bucket, recursive=True)
    for parquet_file in parquet_files:
        if parquet_file.object_name == "yellow_tripdata_2023-01.parquet":
            try:
                if not client.stat_object(bucket, parquet_file.object_name):
                    print(f"Object {parquet_file.object_name} does not exist in bucket {bucket}")
                    continue

                response = client.get_object(bucket, parquet_file.object_name)
                for _ in range(3):  # Retry up to 3 times
                    try:
                        parquet_df = pd.read_parquet(BytesIO(response.data), engine='pyarrow')
                        break
                    except http.client.IncompleteRead:
                        print("Incomplete read, retrying...")
                else:  # No break, raise an error
                    raise RuntimeError("Failed to read data after 3 attempts")

                clean_column_name(parquet_df)
                if not write_data_postgres(parquet_df, db_config):
                    del parquet_df
                    gc.collect()
                    return

                del parquet_df
                gc.collect()
            except Exception as e:
                print(f"Error processing parquet file: {e}")
                return


if __name__ == '__main__':
    sys.exit(main())