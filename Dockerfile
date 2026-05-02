FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for building native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain + wasm32-wasip1 target for Rust strategy compilation
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    && . "$HOME/.cargo/env" \
    && rustup target add wasm32-wasip1

# Make cargo available on PATH for all subsequent RUN and CMD steps
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy only what's needed for pip install (leverage Docker cache)
COPY pyproject.toml /app/

# Copy source code
COPY src/ /app/src/

# Accept version from CI (used by setuptools-scm since .git is not in the build context)
ARG VERSION=0.0.0.dev0

# Install the package with all optional dependencies (JS + Wasm sandboxes)
RUN SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION} pip install --no-cache-dir '.[all]'

# Create default data directory
RUN mkdir -p /app/data

# Expose the default port
EXPOSE 8765

# Start the server bound to all interfaces
CMD ["agent-pitch", "serve", "--host", "0.0.0.0", "--port", "8765", "--data-dir", "/app/data"]
