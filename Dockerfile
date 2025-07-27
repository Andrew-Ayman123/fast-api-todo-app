# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster package management
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy pyproject.toml first for better layer caching
COPY pyproject.toml ./

# Create virtual environment and install dependencies
RUN uv venv .venv
RUN . .venv/bin/activate

# Copy application code
COPY . .

# Install application dependencies
RUN uv pip install -e .
RUN uv pip install pytest pytest-cov pre-commit alembic

# Expose port
EXPOSE 8000

# Default command
CMD ["uv", "run", "run.py"]