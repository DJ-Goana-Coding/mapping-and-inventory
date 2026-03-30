# Unify all Dockerfiles to Python 3.12
echo "🔧 Patching Dockerfile for high-performance libraries..."
cat << 'DOCKER' > ~/ARK_CORE/Dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl git rclone && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
DOCKER

# Update requirements to remove pyarrow (offload to cloud)
sed -i '/pyarrow/d' ~/ARK_CORE/requirements.txt

echo "✅ Fleet patched. Ready for broadcast."
