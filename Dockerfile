# Use a lightweight python image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /workspace

# Run server.py as the entry point
ENTRYPOINT ["python3", "server.py"]
