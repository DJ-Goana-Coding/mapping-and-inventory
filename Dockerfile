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
    data/coding_agent_output data/vector_store data/master_harvest

# Ensure the multi-process launcher is executable in the image.
RUN chmod +x scripts/start_hub.sh

# Streamlit faceplate (HF Space user-facing) on 7860.
# FastAPI sidecar (/v1/ingest, /v1/query, /v1/system/status) on 10000 —
# the SOVEREIGN_HUD_ALIGNMENT v26.59 PORT_RESONANCE_WELD frequency.
EXPOSE 7860
EXPOSE 10000

# Multi-process weld: FastAPI sidecar + Streamlit HUD.
CMD ["bash", "scripts/start_hub.sh"]
