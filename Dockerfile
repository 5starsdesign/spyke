FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash appuser
WORKDIR /app

# Kopieer eerst requirements-bestanden
COPY requirements.txt requirements-dev.txt /app/

# Installeer requirements (prod én optioneel dev)
ARG INSTALL_DEV=false
RUN pip install --no-cache-dir -r requirements.txt && \
    if [ "$INSTALL_DEV" = "true" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

# Kopieer startscript
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

USER appuser
EXPOSE 8000
CMD ["./startup.sh"]
