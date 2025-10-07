# airflow-orchestrator/Dockerfile
FROM apache/airflow:2.9.2

COPY airflow_requirements.txt /opt/airflow/airflow_requirements.txt
RUN pip install --no-cache-dir -r /opt/airflow/airflow_requirements.txt
