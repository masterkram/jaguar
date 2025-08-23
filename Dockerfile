# Use Python 3.13 as base image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Basic tools
    curl \
    wget \
    git \
    # Ripgrep
    ripgrep \
    # JQ for JSON processing
    jq \
    # Find (included in findutils)
    findutils \
    # Dependencies for Unstructured
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-spa \
    libreoffice \
    # Build tools for some Python packages
    gcc \
    g++ \
    build-essential \
    # Additional libraries
    libxml2-dev \
    libxslt-dev \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    # Clean up to reduce image size
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pandoc (specific version for better compatibility, architecture-aware)
RUN ARCH=$(dpkg --print-architecture) && \
    if [ "$ARCH" = "amd64" ]; then \
        PANDOC_ARCH="amd64"; \
    elif [ "$ARCH" = "arm64" ]; then \
        PANDOC_ARCH="arm64"; \
    else \
        echo "Unsupported architecture: $ARCH" && exit 1; \
    fi && \
    wget https://github.com/jgm/pandoc/releases/download/3.1.8/pandoc-3.1.8-1-${PANDOC_ARCH}.deb \
    && dpkg -i pandoc-3.1.8-1-${PANDOC_ARCH}.deb \
    && rm pandoc-3.1.8-1-${PANDOC_ARCH}.deb

# Install uv for fast Python package management
RUN pip install uv

# Set working directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/uploads /app/processed

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv
RUN uv sync --no-dev

# Copy application code
COPY main.py ./

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Ensure uv can access the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Run the application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
