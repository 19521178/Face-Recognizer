# Use the official lightweight Python image
# FROM --platform=linux/amd64 python:3.11-slim

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install python-dev for linux core
RUN apt-get update && apt-get install -y libssl-dev libffi-dev g++ python3.11-dev

# Copy the requirements file
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["flask", "run"]

