# Use Python 3.12 slim image as base
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    --no-install-recommends ca-certificates\
    && rm -rf /var/lib/apt/lists/*

# Parse and report everything in UTC unless the operator overrides it.
ENV TZ=UTC \
    PYTHONUNBUFFERED=1 \
    THE_COUNT_CONFIG_FILE=/etc/thecount/thecount.conf \
    LOG_LEVEL=INFO \
    LOG_FILE=/var/log/thecount/thecount.log

# Python dependencies for the extractors.
# Copy package files for installation
COPY pyproject.toml README.md ./
COPY thecount/ ./thecount/

# Install only the package with core dependencies (no optional dependencies)
RUN pip install --no-cache-dir .

# Create a non-root user
RUN useradd --shell /bin/bash monitoring
RUN chown -R monitoring:monitoring /app
USER monitoring

ENV THE_COUNT_SOURCE_USERNAME=NOT_SET \
    THE_COUNT_SOURCE_PASSWORD=NOT_SET \
    THE_COUNT_SOURCE_HOST=NOT_SET \

    THE_COUNT_SINK_USERNAME=NOT_SET \
    THE_COUNT_SINK_PASSWORD=NOT_SET \
    THE_COUNT_SINK_HOST=NOT_SET


# Set the entrypoint to your package's main module
ENTRYPOINT ["python", "-m", "thecount"]

# Default command (can be overridden)
CMD ["--help"]
