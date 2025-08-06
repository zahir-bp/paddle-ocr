FROM python:3.11-slim

# Create app directory
WORKDIR /app

# Copy files
COPY . /app

# Install Python dependencies
RUN pip install -r requirements.txt && \
    pip install \
        opencv-contrib-python==4.6.0.66 --only-binary :all: && \
    pip install \
        paddlepaddle -f https://www.paddlepaddle.org.cn/whl/paddle_cpu.html && \
    pip install --prefer-binary paddleocr>=2.0.1 Flask==2.3.0

# Expose Flask port
EXPOSE 5000

# Run the app (in production)
CMD ["python3.11", "app.py"]
