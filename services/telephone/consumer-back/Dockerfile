FROM python:3.10-alpine AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.10-alpine

COPY --from=builder /install /usr/local

WORKDIR /app
COPY . .

CMD ["uvicorn", "consumer-back:app", "--host", "0.0.0.0", "--port", "3000"]
