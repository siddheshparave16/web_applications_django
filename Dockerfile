# -- Build Stage ---
FROM python:3.12-slim AS builder

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.0.1 
    
# Update PATH after defining POETRY_HOME
ENV PATH="$POETRY_HOME/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=taskmanager.production

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN apt-get update\
    && apt-get install -y --no-install-recommends curl libpq-dev

RUN pip install "poetry==$POETRY_VERSION"

# Copy the project files into the builder stage
WORKDIR /app
COPY pyproject.toml poetry.lock* /app/

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

# Copy the rest of the application's code
COPY taskmanager /app

# Collect static files
RUN poetry run python manage.py collectstatic --noinput
