FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/main.py .

EXPOSE 8000 6379

CMD ["uvicorn", "main:app", "--port", "8000", "--host", "0.0.0.0"]
