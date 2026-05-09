FROM python:3.9-slim
WORKDIR /app
RUN pip install --no-cache-dir boto3 websockets redis requests
COPY ingestor.py .
ENV PYTHONUNBUFFERED=1
CMD ["python", "ingestor.py"]