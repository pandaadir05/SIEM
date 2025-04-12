# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file (relative to root context)
COPY requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn prometheus_flask_exporter

# Copy the backend_api directory contents (relative to root context)
COPY ./ui/backend_api /app/ui/backend_api
# Copy the shared config.py (relative to root context)
COPY config.py /app/config.py
# Copy rbac.py from its actual location (relative to root context)
COPY ./ui/backend_api/rbac.py /app/rbac.py

# Make port 5000 available
EXPOSE 5000

# Define environment variable
ENV PYTHONUNBUFFERED=1
# Add current dir to PYTHONPATH so imports work relative to /app
ENV PYTHONPATH "${PYTHONPATH}:/app"
# FLASK_APP is set via docker-compose environment section

# Run gunicorn when the container launches
# Path to app object is now relative to /app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "ui.backend_api.app:app"]
