from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.sensors.bigquery import BigQueryTableExistenceSensor
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.providers.google.cloud.operators.automl import AutoMLBatchPredictOperator
from airflow.models import Variable
from datetime import datetime
import pendulum
import arrow

local_tz = pendulum.timezone('Asia/Hong_Kong')

default_args = {
    'retries': 0,
    'catchup': False,
    'start_date': datetime(2022, 6, 18, 21, 0, tzinfo=local_tz),
    'email': [Variable.get("recipient_address")],
    'email_on_failure': False,
}

project_id = 'adroit-hall-301111'
dataset_id = 'demo'
region = 'us-central1' ## try passing this as default args?
       
with DAG('dataproc_automl_backup', description='',
        schedule_interval='0 22 * * *',
        default_args=default_args) as dag:
         
    t1 = BigQueryInsertJobOperator(
        task_id='load_bq_table_append',
        # Refer to this for configuration specification 
        configuration={
            'query': {
                'query': 'SELECT * FROM `adroit-hall-301111.demo.automl_pred_input`',
                'destinationTable': {
                    "projectId": 'adroit-hall-301111',
                    "datasetId": 'demo',
                    "tableId": 'pubsub_dataflow'
                },
                'writeDisposition': 'WRITE_TRUNCATE',
                'createDisposition': 'CREATE_IF_NEEDED',
                'useLegacySql': False
                }
            }
        )

    t2 = DataprocCreateBatchOperator(
      task_id='feature_engineering',
      project_id=project_id,
      region=region,
      batch_id=f'batch_{round(arrow.utcnow().timestamp())}',
      batch={
        "pysparkBatch": {
          "jarFileUris": [
            "gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.25.0.jar"
          ],
          "mainPythonFileUri": "gs://dataproc-staging-us-central1-712368347106-boh5iflc/notebooks/jupyter/MLinPython/pyspark/pyspark_batch.py"
        },
        "labels": {},
        "name": "projects/adroit-hall-301111/locations/us-central1/batches/batch-0478",
        "runtimeConfig": {
          "properties": {
            "spark.executor.instances": "2",
            "spark.driver.cores": "4",
            "spark.executor.cores": "4",
            "spark.app.name": "projects/adroit-hall-301111/locations/us-central1/batches/batch-e3c0"
          }
        },
        "environmentConfig": {
          "executionConfig": {
            "subnetworkUri": "default"
          }
        }
      }
    )

    t3 = BigQueryTableExistenceSensor(
      task_id='polling',
      project_id=project_id,
      dataset_id ='demo',
      table_id='automl_pred_input'
    )

    t4 = AutoMLBatchPredictOperator(
      task_id = 'batch_predict_task',
      project_id=project_id,
      location=region,
      model_id='projects/adroit-hall-301111/locations/us-central1/models/ga4_sample',
      input_config={
        "bigquerySource": {
          "inputUri": "bq://adroit-hall-301111.demo.automl_pred_input"
          }
        },
      output_config={
        "bigqueryDestination": {
          # If defined at project(dataset) level, a dataset(table) will be created under the resource concerned. Cannot be defined at table level
          "outputUri": "bq://adroit-hall-301111.demo"
          },
        }
    )

    t1 >> t2 >> t3 >> t4


