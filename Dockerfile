# Use the Debian slim image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the Python script to the container
COPY maxscale_exporter.py /app/

# Install required Python dependencies
RUN pip install --no-cache-dir aiohttp prometheus-client

# Expose the port for Prometheus metrics
EXPOSE 8000

# Define the command to run the exporter
CMD ["python", "/app/maxscale_exporter.py"]
