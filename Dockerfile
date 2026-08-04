FROM python:3.11-slim

# Install ffmpeg & system dependencies for cloud processing
RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .
COPY index.html .

EXPOSE 9191

# Dynamically bind to the PORT environment variable provided by Render/Railway/Cloud host
CMD ["sh", "-c", "gunicorn server:app --bind 0.0.0.0:${PORT:-9191} --workers 2 --timeout 120"]
