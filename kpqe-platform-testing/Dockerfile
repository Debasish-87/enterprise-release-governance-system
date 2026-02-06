FROM python:3.12-slim

WORKDIR /app

COPY metrics/kpqe_metrics.py /app/
COPY quality_policy.md /app/

RUN pip install kubernetes prometheus_client

EXPOSE 8000

CMD ["python", "kpqe_metrics.py"]
