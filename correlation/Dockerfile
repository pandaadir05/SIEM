# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file (now relative to root context)
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the correlation directory contents (relative to root context)
COPY ./correlation /app/correlation
# Copy the shared config.py (relative to root context)
COPY config.py /app/config.py
# Copy the rules directory (relative to root context)
COPY ./rules /app/rules

# Define environment variable
ENV PYTHONUNBUFFERED=1
# Add current dir to PYTHONPATH so imports work relative to /app
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Run correlation_engine.py when the container launches
# Module path remains the same as code is now in /app/correlation
CMD ["python", "-m", "correlation.correlation_engine"]
