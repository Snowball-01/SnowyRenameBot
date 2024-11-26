# Use the official Python 3.10-slim image for a smaller base
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies and clean up to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to the latest version
RUN python -m pip install --upgrade pip

# Copy only the requirements file to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Specify the command to run your bot script
CMD ["python", "bot.py"]
