FROM python:3.12-slim
WORKDIR /app

# Install system dependencies for ML workloads
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    rclone \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port for Streamlit
EXPOSE 7860

# Run Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
