# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

RUN apt-get update \
    && apt-get install -y ffmpeg \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY src/ ./src/

RUN mkdir -p /app/credentials

# Expose the required port
EXPOSE 8080

# Run the bot script
CMD ["python", "src/bot.py"]