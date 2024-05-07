from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.sensors.bigquery import BigQueryTableExistenceSensor
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.providers.google.cloud.operators.vertex_ai.batch_prediction_job import CreateBatchPredictionJobOperator
from airflow.models import Variable
from datetime import datetime
import pendulum
import arrow

local_tz = pendulum.timezone('Asia/Hong_Kong')

default_args = {
    'retries': 0,
    'catchup': False,
    'start_date': datetime(2022, 6, 15, 21, 0, tzinfo=local_tz),
    'email': [Variable.get("recipient_address")],
    'email_on_failure': False,
}

project_id = 'XXXXXXX'
dataset_id = 'demo'
region = 'us-central1' ## try passing this as default args?

with DAG('dataproc_automl', description='',
        schedule_interval='0 22 * * *',
        default_args=default_args) as dag:
         
    t1 = BigQueryInsertJobOperator(
        task_id='load_bq_table_append',
        # Refer to this for configuration specification 
        configuration={
            'query': {
                'query': 'QUERY',
                'destinationTable': {
                    "projectId": 'PROJECT_ID',
                    "datasetId": 'DATASET_ID',
                    "tableId": 'TABLE_ID'
                },
                'writeDisposition': 'WRITE_TRUNCATE',
                'createDisposition': 'CREATE_IF_NEEDED',
                'useLegacySql': False
                }
            }
        )

    batch_id = f'batch-{round(arrow.utcnow().timestamp())}'
    t2 = DataprocCreateBatchOperator(
      task_id='feature_engineering',
      project_id=project_id,
      region=region,
      batch_id=batch_id,
      batch={
          "pyspark_batch": {
            "jar_file_uris": [
              "gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.25.0.jar"
            ],
            "main_python_file_uri": "PY_FILE_LOCATION_IN_GCS"
          },
          "labels": {},
          "name": f"projects/{project_id}/locations/{region}/batches/{batch_id}",
          "runtime_config": {
            "properties": {
              "spark.executor.instances": "2",
              "spark.driver.cores": "4",
              "spark.executor.cores": "4",
              "spark.app.name": f"projects/{project_id}/locations/{region}/batches/{batch_id}"
            }
          },
          "environment_config": {
            "execution_config": {
              "subnetwork_uri": "default"
            }
          }
        }
    )

    t3 = CreateBatchPredictionJobOperator(
      task_id = 'batch_predict_task',
      project_id=project_id,
      region=region,
      model_name=f'projects/{project_id}/locations/{region}/models/6486577644157534208',
      job_display_name='test',
      predictions_format='bigquery',
      bigquery_source=f"bq://{project_id}.DATASET.TABLE",
      bigquery_destination_prefix=f'bq://{project_id}.DATASET',
    )

    t1 >> t2 >> t3


