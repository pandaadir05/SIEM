# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file (relative to root context)
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the consumer directory contents (relative to root context)
COPY ./consumer /app/consumer
# Copy the shared config.py (relative to root context)
COPY config.py /app/config.py

# Define environment variable
ENV PYTHONUNBUFFERED=1
# Add current dir to PYTHONPATH so imports work relative to /app
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Run indexer.py when the container launches
# Path is now relative to /app
CMD ["python", "consumer/indexer.py"]
