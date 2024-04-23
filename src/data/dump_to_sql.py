import gc
import sys
from xmlrpc.client import ResponseError
import io
import pandas as pd
from minio import Minio
from sqlalchemy import create_engine


def write_data_postgres(dataframe: pd.DataFrame) -> bool:
    """
    Dumps a Dataframe to the DBMS engine

    Parameters:
        - dataframe (pd.Dataframe) : The dataframe to dump into the DBMS engine

    Returns:
        - bool : True if the connection to the DBMS and the dump to the DBMS is successful, False if either
        execution is failed
    """
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
    try:
        engine = create_engine(db_config["database_url"])
        with engine.connect():
            success: bool = True
            print("Connection successful! Processing parquet file")
            dataframe.to_sql(db_config["dbms_table"], engine, index=False, if_exists='append')

    except Exception as e:
        success: bool = False
        print(f"Error connection to the database: {e}")
        return success

    return success


def clean_column_name(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Take a Dataframe and rewrite it columns into a lowercase format.
    Parameters:
        - dataframe (pd.DataFrame) : The dataframe columns to change

    Returns:
        - pd.Dataframe : The changed Dataframe into lowercase format
    """
    dataframe.columns = map(str.lower, dataframe.columns)
    return dataframe


def main() -> None:
    client = Minio(
        "localhost:9000",
        secure=False,
        access_key="minio",
        secret_key="minio123"
    )
    bucket: str = "taxi"
    found = client.bucket_exists(bucket)
    if not found:
        print(f"Bucket {bucket} does not exist")
        return

    print(f"Bucket {bucket} already exists")

    # Loop through the parquet files and write them to the database
    parquet_files = client.list_objects(bucket, recursive=True)

    for parquet_file in parquet_files:
        try:
            data = client.get_object(bucket, parquet_file.object_name)
            data_bytes = io.BytesIO(data.read())
            parquet_df: pd.DataFrame = pd.read_parquet(data_bytes, engine='pyarrow')

            clean_column_name(parquet_df)
            if not write_data_postgres(parquet_df):
                del parquet_df
                gc.collect()
            else:
                return
        except ResponseError as err:
            print(err)


if __name__ == '__main__':
    sys.exit(main())
