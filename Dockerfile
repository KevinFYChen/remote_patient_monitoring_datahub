# ---------- build stage ----------
FROM python:3.12-slim-bookworm AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /build
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# ---------- runtime stage ----------
FROM python:3.12-slim-bookworm
ENV PYTHONPATH=/opt/python/lib/python3.12/site-packages:${PYTHONPATH}
ENV PATH=/opt/python/bin:${PATH}
COPY --from=builder /install /opt/python

WORKDIR /app
COPY . .

# Default command to run Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]