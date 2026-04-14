FROM nvidia/cuda:12.3.2-cudnn9-devel-ubuntu22.04

# Install OS packages and Node.js 20 for the frontend
RUN apt-get update && apt-get install -y \
    curl git git-lfs python3-pip python3-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Upgrade Python packaging tools for modern wheel compatibility
RUN pip install --no-cache-dir --upgrade pip setuptools

WORKDIR /app

# Install frontend dependencies
COPY face/package*.json ./face/
RUN cd face && npm install

# Install backend dependencies
COPY requirements.txt .
# NumPy >= 2.1.0 is required for modern Python wheel compatibility
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Start frontend and backend processes
CMD (cd face && npm run start) & (uvicorn main:app --host 0.0.0.0 --port 7860)
