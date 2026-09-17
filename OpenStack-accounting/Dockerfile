# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    --no-install-recommends ca-certificates\
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
# Need to create a home directory for pip to create ~/.local or ~/.cache whilst building
RUN useradd --create-home --shell /bin/bash monitoring
USER monitoring

WORKDIR /app
# Python dependencies for the extractors.

# Copy package files for installation
COPY pyproject.toml README.md ./
COPY thecount/ ./thecount/

# Install only the package with core dependencies (no optional dependencies)
RUN pip install --no-cache-dir .

# Parse and report everything in UTC unless the operator overrides it.
ENV TZ=UTC \
    PYTHONUNBUFFERED=1 \
    THE_COUNT_CONFIG_FILE=/etc/thecount/thecount.conf \
    LOG_LEVEL=INFO \
    LOG_FILE=/var/log/thecount/thecount.log

# Set the entrypoint to your package's main module
ENTRYPOINT ["python", "-m", "thecount"]

# Default command (can be overridden)
CMD ["--help"]
