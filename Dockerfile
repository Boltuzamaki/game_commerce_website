# Use an official Python slim base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements.txt file first to leverage Docker caching for dependencies
COPY requirements.txt .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (including frontend/main.py) into the container
COPY . .

# Expose the port on which your application runs
EXPOSE 5000

# Command to run the Python application
CMD ["python", "frontend/main.py"]
