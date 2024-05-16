from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from functions.DAG017.src.functions.enviar_correos import EnviarCorreos
from functions.DAG017.src.api.api_dynamic import ApiDynamics
from functions.DAG017.src.functions.enviar_correo_cliente import EnviarCorreosCli
from functions.DAG017.app import execute_application

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email": ["cristian.espinoza@terranovatrading.com.pe"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def execute():
    try:
        execute_application(ApiDynamics, EnviarCorreos, EnviarCorreosCli)
    except Exception as e:
        print(f"No sirve amigo: {e}")
with DAG(
    "DAG_validador_extractos",
    default_args=default_args,
    description="VALIDADOR DE EXTRACTOS",
    schedule_interval="0 8,14 * * *",
    start_date=datetime(2024, 5, 13, 8, 0, 0),
    tags=["DAG_validador_extractos"],
) as dag:
    scrape_task = PythonOperator(task_id="ejecutar_aplicacion", python_callable=execute)


