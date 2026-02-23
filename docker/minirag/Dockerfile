# Use the official uv image with python 3.12-slim
FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

# Set the working directory
WORKDIR /app

# Install additional system dependencies for lxml and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libavif-dev pkg-config \
    libjpeg-dev \
    gcc unzip zip \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy your requirements
COPY src/requirements.txt .

# Install dependencies using uv
# --system tells uv to install into the image's python environment
RUN uv pip install -r requirements.txt --system

# Copy the rest of your code
COPY src/ .

# create a directory structure for alembic
RUN mkdir -p /app/models/db_schemes/minirag/

# Copy config and entrypoint
COPY docker/minirag/alembic.ini /app/models/db_schemes/minirag/alembic.ini
COPY docker/minirag/entrypoint.sh /entrypoint.sh
# Fix permissions
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]

# Expose FastAPI port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

