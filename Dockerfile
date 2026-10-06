FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gateway.py .
COPY test_gateway.py .

EXPOSE 8080

ENV PORT=8080
ENV API_KEY=dev-key-change-in-production
ENV RATE_LIMIT_WINDOW=60
ENV RATE_LIMIT_MAX=100

CMD ["python3", "gateway.py"]
