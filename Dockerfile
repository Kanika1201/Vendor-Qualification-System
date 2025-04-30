# Dockerfile
# Containerizes the FastAPI app with all dependencies.
# Builds a portable image that can be run using:
#   docker build -t vendor-qualification-system .
#   docker run -d -p 8000:8000 vendor-qualification-system
# Author: Kanika Saxena

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
