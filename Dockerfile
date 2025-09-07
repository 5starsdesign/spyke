FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash appuser
WORKDIR /app

# requirements
COPY requirements.txt requirements.txt /app/
COPY requirements-dev.txt requirements-dev.txt /app/

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r requirements-dev.txt

COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

USER appuser
EXPOSE 8000
CMD ["./startup.sh"]
