# -- Build Stage ---
FROM python:3.12-slim AS builder

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.0.1 \
    POETRY_HOME="/opt/poetry"
    
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
    && poetry install --only main --no-interaction --no-ansi --no-root

# Copy the rest of the application's code
COPY taskmanager /app

# Collect static files
RUN poetry run python manage.py collectstatic --noinput


# --- Production Stage ---

# Define the base image for the production stage

FROM python:3.12-slim AS production

# Copy virtual env and other necessary files from builder stage
# Copy installed packeges and binaries from builder stage
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# set the working directory in the container
WORKDIR /app 

# Set user to use when running the image
#UID 1000 is often the default user
# Create and switch to non-root user
RUN addgroup --system django && \
    adduser --system --ingroup django django && \
    chown -R django:django /app

USER django

# Start Gunicorn with a configuration file
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "taskmanager.wsgi"]

# Inform Docker that the container listens on the specified network ports at runtime
EXPOSE 8000
