FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies separately so Docker can cache this layer.
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 botuser
COPY --chown=botuser:botuser bot.py ./
USER botuser

# Discord bots are persistent workers; no inbound HTTP port is required.
CMD ["python", "-u", "bot.py"]
