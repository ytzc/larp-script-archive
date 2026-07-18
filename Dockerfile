# Use a lightweight python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /workspace

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Define default environment variables
ENV PORT=8000
ENV WEB_DIR=docs

# Run server.py as the entry point
ENTRYPOINT ["python3", "server.py"]
