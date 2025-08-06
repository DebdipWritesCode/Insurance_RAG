# Use a lightweight Python image
FROM python:3.11-slim

# Install system-level dependencies (Tesseract, fonts, etc.)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Expose the port for FastAPI (Railway uses PORT env)
EXPOSE 8000

# Start the FastAPI app with uvicorn
ENTRYPOINT ["/bin/sh", "-c"]
CMD ["uvicorn main:app --host=0.0.0.0 --port=${PORT:-8000}"]
