FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /app/
COPY entrypoint.sh /app/

RUN mkdir -p /app/staticfiles /app/mediafiles /app/data \
    && addgroup --system django \
    && adduser --system --ingroup django django \
    && chmod +x /app/entrypoint.sh \
    && chown -R django:django /app

USER django

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "MSF_Tool.wsgi:application"]