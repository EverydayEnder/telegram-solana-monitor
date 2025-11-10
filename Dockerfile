FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    telethon==1.36.0 \
    requests==2.31.0 \
    aiohttp==3.9.1

# Copy application
COPY telegram_monitor.py .

# Create volume mount point for session persistence
RUN mkdir -p /data

VOLUME ["/data"]

# Expose health check port
EXPOSE 8000

# Health check for Coolify
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()" || exit 1

# Run with unbuffered output
CMD ["python", "-u", "telegram_monitor.py"]
