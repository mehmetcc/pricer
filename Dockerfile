# Use Python 3.13 as the base image (future version, placeholder for now)
# Replace with the official Python 3.13 image when it becomes available
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry for dependency management
RUN pip install --no-cache-dir poetry

# Copy the application dependencies file
COPY pyproject.toml poetry.lock ./

# Install dependencies without dev packages
RUN poetry install --no-root

# Copy the rest of the application code
COPY src ./src

# Set environment variables to configure Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/src"

# Expose the application port
EXPOSE 9990

# Set the command to run the app
CMD ["poetry", "run", "start"]
