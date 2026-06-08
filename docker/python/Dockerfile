FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --no-dev

# Copy source code
COPY python/ ./python/
COPY rust/ ./rust/

# Set Python path
ENV PYTHONPATH=/app/python

EXPOSE 8000

CMD ["uv", "run", "python", "-m", "nsaca.main", "--help"]
