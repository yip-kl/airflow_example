import time
from datetime import datetime, timedelta
import pendulum
import pprint

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow import macros

local_tz = pendulum.timezone('Asia/Hong_Kong')

default_args = {
    "start_date": datetime(2024, 5, 7, tzinfo=local_tz),
    "retries": 0
}

def direct_print_will_not_work():
    print("""ds: {{ ds }}""")

def print_context(logical_date, **kwargs):
    # See more here https://airflow.apache.org/docs/apache-airflow/1.10.6/howto/operator/python.html
    # Different Operator has different ways of retrieving context. On the contrary, BashOperator "natively" uses Jinja templating 
    pprint.pp(kwargs)
    logical_date_to_hkt = logical_date + timedelta(hours=8)
    print(logical_date_to_hkt.strftime("%Y-%m-%d %H:%M:%S"))
    return 'Whatever you return gets printed in the logs'

with DAG("simple_dag", default_args=default_args, schedule_interval="* * * * *", catchup= False) as dag:
    t1 = PythonOperator(task_id="py_direct_print", python_callable=direct_print_will_not_work)
    t2 = PythonOperator(task_id="py_context", python_callable=print_context, provide_context=True)
    t3 = BashOperator( task_id='bash_logical_date_formatted', bash_command="""echo {{ logical_date.strftime("%Y-%m-%d %H:%M:%S") }}""")
    