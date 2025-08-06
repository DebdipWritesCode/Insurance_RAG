# Use a lightweight Python image
FROM python:3.11-slim

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    poppler-utils \
    libreoffice \
    curl \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Expose port for FastAPI (optional, based on platform)
EXPOSE 8000

# Start your FastAPI app
CMD ["python", "main.py"]