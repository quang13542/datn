from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.utils.trigger_rule import TriggerRule

with DAG(
    "update_pipeline",
    default_args={
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    description="A simple DAG",
    schedule=timedelta(days=1),
    start_date=datetime(2024, 1, 1),
    tags=["etl"],
) as dag:

    TopCV_button_name_check = BashOperator(
        task_id="TopCV_button_name_check",
        bash_command="python3 crawler_datn/TopCV_update_status.py",
    )

    TopDev_url_check = BashOperator(
        task_id="TopDev_url_check",
        bash_command="python3 crawler_datn/TopDev_update_status.py",
        trigger_rule=TriggerRule.ONE_FAILED,
    )

    ITViec_url_check = BashOperator(
        task_id="ITViec_url_check",
        bash_command="python3 crawler_datn/ITViec_update_status.py",
    )

    ITjobs_button_name_check = BashOperator(
        task_id="ITjobs_button_name_check",
        bash_command="python3 crawler_datn/ITjobs_update_status.py",
    )

    update_task = BashOperator(
        task_id="update",
        bash_command="python3 main.py upsert_data",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    TopCV_button_name_check >> update_task
    TopDev_url_check >> update_task
    ITViec_url_check >> update_task
    ITjobs_button_name_check >> update_task
    
