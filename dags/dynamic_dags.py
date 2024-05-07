from datetime import datetime
from airflow.decorators import dag, task
from airflow import DAG
import pendulum

local_tz = pendulum.timezone('Asia/Hong_Kong')

files_list = [
    {'name': 'file1', 'destination': 'dest1', 'start_date': datetime(2022, 1, 1, tzinfo=local_tz), 'schedule_interval': '0 22 * * *'},
    {'name': 'file2', 'destination': 'dest2', 'start_date': datetime(2023, 1, 1, tzinfo=local_tz), 'schedule_interval': '0 9 * * *'},
    # Add more files and destinations as needed
]

def create_dag(file_name, file_destination, dag_id, start_date, schedule_interval):
    
    @dag(dag_id=dag_id, start_date=start_date, schedule_interval=schedule_interval, catchup=False)
    def dynamic_generated_dag():
        @task
        def load_file(name, destination):
            print(f"Loaded {name} to {destination}")

        load_file(file_name, file_destination)

    generated_dag = dynamic_generated_dag()

    return generated_dag

for file in files_list:

    # DAG arguments
    dag_id = f"dynamic_generated_dag_{file['name']}"
    start_date=file['start_date']
    schedule_interval=file['schedule_interval']

    # Task arguments
    file_name = file['name']
    file_destination = file['destination']

    globals()[dag_id] = create_dag(file_name, file_destination, dag_id, start_date, schedule_interval)