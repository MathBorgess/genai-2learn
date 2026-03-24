FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app/src

EXPOSE 8001

CMD ["gunicorn", "-b", "0.0.0.0:8001", "--workers", "2", "--timeout", "60", "app:create_app()"]
