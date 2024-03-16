# Use Python 3.10 as base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update pip
RUN pip install --no-cache-dir --upgrade pip

# Install Chrome and ChromeDriver dependencies
RUN apt-get update && apt-get install -y wget gnupg curl unzip

# Install Chrome
RUN curl -sSL https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.198-1_amd64.deb -o chrome.deb
RUN dpkg -i chrome.deb || apt-get install -fy

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION=114.0.5735.90; \
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver

# Clean up
RUN rm chrome.deb /tmp/chromedriver.zip

# Set working directory
WORKDIR /usr/src/app

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the working directory
COPY . .
