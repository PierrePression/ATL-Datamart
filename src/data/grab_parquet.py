import sys
from datetime import datetime, timedelta

from minio import Minio
import requests
import pandas as pd
from io import StringIO
import os
import stat


def main():
    grab_data()
    write_data_minio()


CHUNK_SIZE = 1024
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-{month}.parquet"
TARGET_DIR = "../../data/raw"

def download_file(url: str, destination_path: str) -> None:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(destination_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        print(f"Saved to {destination_path}")
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

def grab_data() -> None:
    os.makedirs(TARGET_DIR, exist_ok=True)
    months = ['01', '02', '03', '04', '05', '06', '07', '08']

    for month in months:
        file_name = f"yellow_tripdata_2023-{month}.parquet"
        url = BASE_URL.format(month=month)
        destination_path = os.path.join(TARGET_DIR, file_name)

        print(f"Downloading {file_name}...")
        download_file(url, destination_path)


def grab_last_month_data() -> None:
    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_"
    today = datetime.today()
    last_month = today.replace(day=1) - timedelta(days=1)
    year_month = last_month.strftime("%Y-%m")
    url = f"{base_url}{year_month}.csv"
    response = requests.get(url)
    file_content = response.content.decode('utf-8')
    data_frame = pd.read_csv(StringIO(file_content))
    destination = f"yellow_tripdata_{year_month}.parquet"
    file_path = os.path.join("../../data/raw", destination)
    data_frame.to_parquet(file_path)
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)

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
