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
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copy your requirements
COPY src/requirements.txt .

# Install dependencies using uv
# --system tells uv to install into the image's python environment
RUN uv pip install -r requirements.txt --system

# Copy the rest of your code
COPY src/ .

# Expose FastAPI port
EXPOSE 8000

# Command to run the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

