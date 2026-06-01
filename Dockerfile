FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (for layer caching)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code
COPY backend/ .

# Expose Flask port
EXPOSE 5000

# Start: init DB then run Flask
CMD ["sh", "-c", "python migrations/init_db.py && python app.py"]
