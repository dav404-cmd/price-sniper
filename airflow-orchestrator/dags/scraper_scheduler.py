from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
from pathlib import Path

# Make sure Airflow container can find your scraper module
project_root = Path("/opt/smart_pricetracker").resolve()
sys.path.append(str(project_root))

from scraper.scraper_runner_bs4 import run_by_search

default_args = {
    "owner": "nox",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

def log_wrapper(**kwargs):
    query = kwargs.get("query", "iphone")
    print(f" Running scraper for query: {query}")
    run_by_search(query=query, max_pages=50)
    print(f" Completed scraping for: {query}")

with DAG(
    dag_id="daily_iphone_scraper",
    start_date=datetime(2025, 10, 3),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
    description="Scrapes iPhone listings daily using run_by_search",
) as dag:
    scrape_iphone_task = PythonOperator(
        task_id="scrape_iphone_listings",
        python_callable=log_wrapper,
        op_kwargs={"query": "iphone"},
    )
