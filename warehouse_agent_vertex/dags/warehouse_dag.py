from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime
from scripts import etl_bq, forecasting_bq

default_args = {'start_date': datetime(2025, 7, 1)}

with DAG('warehouse_etl', default_args=default_args, schedule_interval='@daily', catchup=False) as dag:

    etl_task = PythonOperator(
        task_id='etl_to_bq',
        python_callable=etl_bq.main
    )

    forecast_task = PythonOperator(
        task_id='forecast_to_bq',
        python_callable=forecasting_bq.main
    )

    build_pairs = BigQueryInsertJobOperator(
        task_id='build_cross_sell_pairs',
        configuration={
            'query': {
                'query': open('scripts/cross_sell_pairs.sql').read()
                          .replace('{{project}}','{{ var.value.gcp_project }}')
                          .replace('{{dataset}}','warehouse'),
                'useLegacySql': False
            }
        }
    )

    etl_task >> forecast_task >> build_pairs
