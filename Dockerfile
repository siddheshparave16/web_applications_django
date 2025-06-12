# --- Build Stage ---
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.0.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    DJANGO_SETTINGS_MODULE=taskmanager.production

# Update PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Create working directory
WORKDIR /app

# Copy only requirements to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Install project dependencies (system-wide)
RUN poetry install --only main --no-root

# Copy the entire application to the working directory
COPY . .

# Verify manage.py exists
RUN test -f /app/taskmanager/manage.py && echo "manage.py exists" || exit 1

# Collect static files
RUN python /app/taskmanager/manage.py collectstatic --noinput


# --- Production Stage ---
FROM python:3.12-slim AS production

# Install runtime dependencies including curl
RUN apt-get update && apt-get install -y --no-install-recommends curl libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages and binaries from builder stage
COPY --from=builder /usr/local /usr/local

# Copy application code from builder stage
COPY --from=builder /app /app

# Set the working directory in the container
WORKDIR /app 

# Create and switch to a non-root user
RUN addgroup --system django && \
    adduser --system --ingroup django django && \
    chown -R django:django /app

USER django

# Start Gunicorn with a configuration file
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "taskmanager.wsgi"]

# Expose the application port
EXPOSE 8000
