FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Environment variables documentation
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json
ENV HUGGINGFACE_TOKEN=""
ENV PIONEER_TRADER_URL=""
ENV PIONEER_AUTH_TOKEN=""
ENV SHADOW_ARCHIVE_PATH=/app/shadow_archive
ENV PORT=8000

# Create shadow archive directory
RUN mkdir -p /app/shadow_archive

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; import requests; sys.exit(0 if requests.get('http://localhost:8000/health', timeout=5).status_code == 200 else 1)" || exit 1

# Expose port for FastAPI
EXPOSE 8000

# Run the application
CMD ["./start.sh"]
