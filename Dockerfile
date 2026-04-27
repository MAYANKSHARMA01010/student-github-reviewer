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

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose the port Streamlit will run on (HF default is 7860)
EXPOSE 7860

# Run the Streamlit app directly
ENTRYPOINT ["streamlit", "run", "ui/app.py", "--server.port=7860", "--server.address=0.0.0.0"]
