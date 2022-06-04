from google.cloud import storage
import os
import glob

def get_dags_bucket(path='/usr/local/airflow/include/credentials/composer_dags_bucket.txt'):
    with open(path) as f:
        lines = f.readlines()
        return lines[0].strip()

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(
        "File {} uploaded to {}.".format(
            source_file_name, destination_blob_name
        )
    )

def upload_dags():
    dags_bucket = get_dags_bucket()
    for filename in glob.glob(os.path.join('dags', '*.py')):
        if 'example' not in filename:
            upload_blob(dags_bucket, filename, f'dags/{os.path.basename(filename)}')

if __name__ == "__main__":
    upload_dags()