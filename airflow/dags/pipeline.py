from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.utils.trigger_rule import TriggerRule


with DAG(
    "ETL",
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

    TopCV_url_crawler_task = BashOperator(
        task_id="TopCV_url_crawler",
        bash_command="python3 crawler_datn/TopCV_url_crawler.py",
    )
    TopCV_post_crawler_task = BashOperator(
        task_id="TopCV_post_crawler",
        bash_command="python3 crawler_datn/TopCV_post_crawler.py",
    )
    extract_TopCV_task = BashOperator(
        task_id="extract_TopCV",
        bash_command="python3 transform_datn/extract_TopCV.py",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    TopDev_url_crawler_task = BashOperator(
        task_id="TopDev_url_crawler",
        bash_command="python3 crawler_datn/TopDev_url_crawler.py",
        trigger_rule=TriggerRule.ONE_FAILED,
    )
    TopDev_post_crawler_task = BashOperator(
        task_id="TopDev_post_crawler",
        bash_command="python3 crawler_datn/TopDev_post_crawler.py",
    )
    extract_TopDev_task = BashOperator(
        task_id="extract_TopDev",
        bash_command="python3 transform_datn/extract_TopDev.py",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    crawl_url_ITViec_task = BashOperator(
        task_id="crawl_url_ITViec",
        bash_command="python3 crawler_datn/ITViec_url_crawler.py",
    )
    ITViec_post_crawler_task = BashOperator(
        task_id="ITViec_post_crawler",
        bash_command="python3 crawler_datn/ITViec_post_crawler.py",
    )
    extract_ITViec_task = BashOperator(
        task_id="extract_ITViec",
        bash_command="python3 transform_datn/extract_ITViec.py",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    crawl_ITjobs_task = BashOperator(
        task_id="crawl_url_ITjobs",
        bash_command="python3 crawler_datn/ITjobs_url_crawler.py",
    )
    ITjobs_post_crawler_task = BashOperator(
        task_id="ITjobs_post_crawler",
        bash_command="python3 crawler_datn/ITjobs_post_crawler.py",
    )
    extract_ITjobs_task = BashOperator(
        task_id="extract_ITjobs",
        bash_command="python3 transform_datn/extract_ITjobs.py",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    combine_task = BashOperator(
        task_id="combine",
        bash_command="python3 main.py combine_data",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    upsert_task = BashOperator(
        task_id="upsert",
        bash_command="python3 main.py upsert_data",
    )

    extract_through_api_task = BashOperator(
        task_id='extract_through_api_task',
        bash_command='python3 crawler_datn/TopDev_post_url_crawler.py',
    )

    TopCV_url_crawler_task >> TopCV_post_crawler_task >> extract_TopCV_task
    extract_TopCV_task >> extract_through_api_task
    TopDev_url_crawler_task >> TopDev_post_crawler_task >> extract_TopDev_task
    extract_TopDev_task >> crawl_url_ITViec_task
    crawl_url_ITViec_task >> ITViec_post_crawler_task >> extract_ITViec_task
    extract_ITViec_task >> crawl_ITjobs_task
    crawl_ITjobs_task >> ITjobs_post_crawler_task >> extract_ITjobs_task

    extract_through_api_task >> [TopDev_url_crawler_task, crawl_url_ITViec_task]

    [extract_TopCV_task, extract_TopDev_task, extract_ITViec_task, extract_ITjobs_task] >> combine_task

    combine_task >> upsert_task