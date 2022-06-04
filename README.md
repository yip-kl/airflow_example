Overview
========

This is a sample project for local Airflow development making use of the `astro` cli. Please refer to [Astronomer's git](https://github.com/astronomer/astro-cli) about how to install astro in the first place

Welcome to Astronomer! This project was generated after you ran 'astro dev init' using the Astronomer CLI. This readme describes the contents of the project, as well as how to run Apache Airflow on your local machine.

Project Contents
================

Your Astro project contains the following files and folders:

- dags: This folder contains the Python files for your Airflow DAGs. By default, this directory includes an example DAG that runs every 30 minutes and simply prints the current date. It also includes an empty 'my_custom_function' that you can fill out to execute Python code.
- Dockerfile: This file contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience. If you want to execute other commands or overrides at runtime, specify them here.
- include: This folder contains any additional files that you want to include as part of your project. It is empty by default.
- packages.txt: Install OS-level packages needed for your project by adding them to this file. It is empty by default.
- requirements.txt: Install Python packages needed for your project by adding them to this file. It is empty by default.
- plugins: Add custom or community plugins for your project to this file. It is empty by default.
- airflow_settings.yaml: Use this local-only file to specify Airflow Connections, Variables, and Pools instead of entering them in the Airflow UI as you develop DAGs in this project.

Deploy Your Project Locally
===========================

1. Start Airflow on your local machine by running 'astro dev start'.

This command will spin up 3 Docker containers on your machine, each for a different Airflow component:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI
- Scheduler: The Airflow component responsible for monitoring and triggering tasks

2. Verify that all 3 Docker containers were created by running 'docker ps'.

Note: Running 'astro dev start' will start your project with the Airflow Webserver exposed at port 8080 and Postgres exposed at port 5432. If you already have either of those ports allocated, you can either stop your existing Docker containers or change the port.

3. Access the Airflow UI for your local Airflow project. To do so, go to http://localhost:8080/ and log in with 'admin' for both your Username and Password.

You should also be able to access your Postgres Database at 'localhost:5432/postgres'.

Deploy Your Project to Astronomer
=================================

If you have an Astronomer account, pushing code to a Deployment on Astronomer is simple. For deploying instructions, refer to Astronomer documentation: https://docs.astronomer.io/cloud/deploy-code/

Contact
=======

The Astronomer CLI is maintained with love by the Astronomer team. To report a bug or suggest a change, reach out to our support team: https://support.astronomer.io/

My notes
========

## Development
- cd to the project root, and use `astro dev start` to spin up the containers while Docker Desktop is active
- To speed up development, attach to webserver container via VSCode Remote Explorer, navigate to `/usr/local/airflow/` and directly update the dags there. This would be picked up by the web server very quickly
- `AIRFLOW__LOGGING__LOGGING_LEVEL` is set as `DEBUG` in the Dockerfile to make debugging easier
- These are useful commands for development:
    - `astro dev restart`: rebuild the container e.g. after you have added new items under requirements.txt
    - `astro dev stop`: pause containers
    - `astro dev kill`: not only stopping the containers, it will also delete all data associated with your local Postgres metadata database, including Airflow Connections, logs, and task history.
- The script `include/dags_to_gcs.py` is for uploading the dags to the dags folder in GCS directly
## Configuration
- Under the webserver container there is a `airflow.cfg` which controls the configuration of Airflow, whose values can be overridden using environment variables, Please see [here](https://airflow.apache.org/docs/apache-airflow/stable/configurations-ref.html) for reference
- Sample environment variables can be referred from `config_samples/sample.env`, copy them to `.env` and update the values as needed
## Connections
- GCP: To connect to GCP for local development, `GOOGLE_APPLICATION_CREDENTIALS` is defined in the .env file for Application Default Credentials, and `AIRFLOW_CONN_GOOGLE_CLOUD_DEFAULT` is also defined so that Airflow can infer conn_id `google_cloud_default` from the Application Default Credentials. Please see [here](https://airflow.apache.org/docs/apache-airflow-providers-google/stable/connections/gcp.html) for more details
    - Alternatively, connection to GCP can be done by explicitly declaring this in Admin -> Connection. A sample ```config_samples/airflow_settings_sample.yaml``` is included to demonstrate how to do this as code. For such update to be effective, please remove the existing connection under Admin -> Connection first, then rebuild the container
- SendGrid: For local development purpose, connections to which is defined in the .env file. If we are using Cloud Composer, it should be done by overriding the Airflow configuration options. See [here](https://cloud.google.com/composer/docs/composer-2/configure-email)
## Triggers
- Scheduled run will happen after 1 scheduled_interval. Say if you created a DAG with start_date = 2010-01-01 and to run 2pm every day, the DAG will run immediately upon getting detected by Airflow even `catchup` is set as False. If you don't to execute it right away, you should set catchup=false and start_date to a future date
- DAG with a future start_date cannot be run. Say if you have a DAG with start_date = 2040-01-01, the tasks included in the DAG won't run even if you trigger the DAG manually
