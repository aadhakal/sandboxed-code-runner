FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including nsjail and Python libraries
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    nsjail \
    libprotobuf23 \
    libnl-route-3-200 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --no-cache-dir \
    flask==2.3.3 \
    gunicorn==21.2.0 \
    numpy==1.24.3 \
    pandas==2.0.3 \
    requests==2.31.0 \
    scipy==1.11.1 \
    matplotlib==3.7.2 \
    seaborn==0.12.2 \
    scikit-learn==1.3.0

# Set working directory
WORKDIR /app

# Copy application file
COPY app.py .

# Create necessary directories with proper permissions
RUN mkdir -p /tmp && chmod 1777 /tmp

# Create non-root user for running the application
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app

# Ensure nsjail is accessible
RUN ln -sf /usr/bin/nsjail /usr/bin/nsjail && chmod +x /usr/bin/nsjail

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60", "app:app"]