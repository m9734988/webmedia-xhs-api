FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY locale ./locale
COPY source ./source
COPY static ./static
COPY LICENSE ./LICENSE
COPY serve.py ./serve.py

EXPOSE 5556

CMD ["python", "serve.py"]
