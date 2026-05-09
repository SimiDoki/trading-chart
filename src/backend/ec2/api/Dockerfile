FROM python:3.9-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn boto3 redis
COPY api_service.py .
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["python", "api_service.py"]