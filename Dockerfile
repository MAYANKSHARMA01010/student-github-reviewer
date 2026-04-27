# Use the official Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Set environment variables
ENV BACKEND_URL=http://localhost:8000
ENV PYTHONUNBUFFERED=1

# Expose the port Streamlit will run on
EXPOSE 7860

# Run the startup script
CMD ["./start.sh"]
