# Use official Python image
FROM python:3.10-slim

# # Prevents Python from buffering stdout/stderr
# ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements first (to leverage Docker cache)
COPY requirements.txt .

# Install system dependencies and Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 5000

# Run with Gunicorn for production
CMD ["python","app.py"]
