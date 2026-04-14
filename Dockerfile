FROM nvidia/cuda:12.3.2-cudnn9-devel-ubuntu22.04

# 1. INSTALL SYSTEM DEPENDENCIES & NODE.JS (The Face)
RUN apt-get update && apt-get install -y \
    curl git git-lfs python3-pip python3-dev \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 2. FIX THE PYTHON GHOST (The Heart)
# We stay on Python 3.12 or upgrade NumPy to avoid the 3.13 build-loop
RUN pip install --no-cache-dir --upgrade pip setuptools

WORKDIR /app

# 3. WELD THE FACE (Next.js / Node.js)
COPY face/package*.json ./face/
RUN cd face && npm install

# 4. WELD THE HEART (Python / Vortex)
COPY requirements.txt .
# CRITICAL: We use NumPy >= 2.1.0 for Python 3.12+ compatibility
RUN pip install --no-cache-dir -r requirements.txt

# 5. COPY THE REST OF THE CITADEL
COPY . .

# 6. IGNITION: Running both Next.js and FastAPI
# We use a simple background execution or a process manager
CMD (cd face && npm run start) & (uvicorn main:app --host 0.0.0.0 --port 7860)
