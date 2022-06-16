from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.models import Variable
from datetime import datetime
import pendulum

local_tz = pendulum.timezone('Asia/Hong_Kong')

default_args = {
    'retries': 0,
    'catchup': False,
    'start_date': datetime(2022, 6, 3, 22, 0, tzinfo=local_tz),
    'email': [Variable.get("recipient_address")],
    'email_on_failure': True,
}
       
with DAG('scheduled_query', description='',
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
                'writeDisposition': 'WRITE_APPEND',
                'createDisposition': 'CREATE_IF_NEEDED',
                'useLegacySql': False
                }
            }
        )