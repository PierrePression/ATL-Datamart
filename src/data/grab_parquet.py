import sys
from datetime import datetime, timedelta

from minio import Minio
import requests
import pandas as pd
import os
from io import StringIO


def main():
    grab_data()
    write_data_minio()


def grab_data() -> None:
    """Grab the data from New York Yellow Taxi

    This method download files of the New York Yellow Taxi from January 2023 to August 2023.

    Files are saved into "../../data/raw" folder
    This methods takes no arguments and returns nothing.
    """
    base_url = "https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_"
    for month in range(1, 9):  # Months from January (1) to August (8)
        year_month = f"2023-{month:02d}"
        url = f"{base_url}{year_month}.csv"
        response = requests.get(url)
        file_content = response.content.decode('utf-8')
        data_frame = pd.read_csv(StringIO(file_content))  # Use StringIO from io
        destination = f"yellow_tripdata_{year_month}.parquet"
        data_frame.to_parquet(os.path.join("../../data/raw", destination))


def grab_last_month_data() -> None:
    """Grab the data from New York Yellow Taxi for the last month

    This method download the file of the New York Yellow Taxi for the last month.

    File is saved into "../../data/raw" folder
    This methods takes no arguments and returns nothing.
    """
    base_url = "https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_"
    today = datetime.today()
    last_month = today.replace(day=1) - timedelta(days=1)
    year_month = last_month.strftime("%Y-%m")
    url = f"{base_url}{year_month}.csv"
    response = requests.get(url)
    file_content = response.content.decode('utf-8')
    data_frame = pd.read_csv(StringIO(file_content))
    destination = f"yellow_tripdata_{year_month}.parquet"
    data_frame.to_parquet(os.path.join("../../data/raw", destination))


def write_data_minio():
    """
    This method put all Parquet files into Minio
    Ne pas faire cette méthode pour le moment
    """
    client = Minio(
        "localhost:9000",
        secure=False,
        access_key="minio",
        secret_key="minio123"
    )
    bucket: str = "taxi"
    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket)
    else:
        print("Bucket " + bucket + " existe déjà")

    for file_name in os.listdir("../../data/raw"):
        if file_name.endswith(".parquet"):
            file_path = os.path.join("../../data/raw", file_name)
            client.fput_object(bucket, file_name, file_path)
            print(f"Uploaded {file_name} to Minio bucket {bucket}")


if __name__ == '__main__':
    sys.exit(main())
