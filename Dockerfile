FROM python:3.11-slim

# Install OS packages needed by the Citadel
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git rclone \
    && rm -rf /var/lib/apt/lists/*

# Upgrade Python packaging tools
RUN pip install --no-cache-dir --upgrade pip setuptools

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create necessary data directories
RUN mkdir -p data/spiritual_intelligence data/tarot_readings data/models \
    data/workers data/datasets data/Mapping-and-Inventory-storage \
    data/coding_agent_output

EXPOSE 7860

# Launch Streamlit faceplate on port 7860
CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
