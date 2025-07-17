# Use an official Python image
FROM python:3.10-slim

# Set environment variables
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# System dependencies
# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install opencv-python-headless flask[async] setuptools paddlepaddle paddleocr requests asyncio typing

# Copy project files
COPY . .

# Expose Flask port
EXPOSE 8080

# Command to run the app
CMD ["python3", "app.py"]
