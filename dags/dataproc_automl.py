from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.sensors.bigquery import BigQueryTableExistenceSensor
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.providers.google.cloud.operators.automl import AutoMLBatchPredictOperator
from airflow.models import Variable
from datetime import datetime
import pendulum
import arrow
from google.cloud import dataproc_v1

local_tz = pendulum.timezone('Asia/Hong_Kong')

default_args = {
    'retries': 0,
    'catchup': False,
    'start_date': datetime(2022, 6, 15, 21, 0, tzinfo=local_tz),
    'email': [Variable.get("recipient_address")],
    'email_on_failure': False,
}

project_id = 'adroit-hall-301111'
dataset_id = 'demo'
region = 'us-central1' ## try passing this as default args?

# Define Dataproc batch, the DataprocCreateBatchOperator rides on the create_batch method (refer to batch_controller) of the dataproc_v1 library,
# which in turns requires a batch class to be defined, see below
# https://github.com/googleapis/python-dataproc/blob/main/google/cloud/dataproc_v1/services/batch_controller/client.py
# https://github.com/googleapis/python-dataproc/blob/main/google/cloud/dataproc_v1/types/batches.py
dataproc_batch = dataproc_v1.Batch()
batch_id = f'batch-{round(arrow.utcnow().timestamp())}'
batch_spec = {
  "pyspark_batch": {
    "jar_file_uris": [
      "gs://spark-lib/bigquery/spark-bigquery-with-dependencies_2.12-0.25.0.jar"
    ],
    "main_python_file_uri": "gs://dataproc-staging-us-central1-712368347106-boh5iflc/notebooks/jupyter/MLinPython/pyspark/pyspark_batch.py"
  },
  "labels": {},
  "name": f"projects/adroit-hall-301111/locations/us-central1/batches/{batch_id}",
  "runtime_config": {
    "properties": {
      "spark.executor.instances": "2",
      "spark.driver.cores": "4",
      "spark.executor.cores": "4",
      "spark.app.name": f"projects/adroit-hall-301111/locations/us-central1/batches/{batch_id}"
    }
  },
  "environment_config": {
    "execution_config": {
      "subnetwork_uri": "default"
    }
  }
}
def set_attr_from_dict(class_obj, dictionary):
    for k, v in dictionary.items():
        setattr(class_obj, k, v)

dataproc_batch = set_attr_from_dict(dataproc_batch, batch_spec)

with DAG('dataproc_automl', description='',
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
      batch_id=batch_id,
      batch=dataproc_batch
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


