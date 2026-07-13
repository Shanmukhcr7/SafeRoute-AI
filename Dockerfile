# Use official Python runtime as a parent image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies required for GeoPandas/Folium and Pyttsx3
RUN apt-get update && apt-get install -y \
    build-essential \
    libgdal-dev \
    espeak \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

# Set Environment Variables for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Command to run the Streamlit application
CMD ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
