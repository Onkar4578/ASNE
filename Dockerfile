# Dockerfile for deploying ASNE on Hugging Face Spaces (Docker SDK)
# HF Spaces expects the app to listen on port 7860 by default.

FROM python:3.12-slim

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face Spaces routes external traffic to port 7860
EXPOSE 7860

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
