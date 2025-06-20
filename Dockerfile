FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Add build argument for environment
ARG ENVIRONMENT=production

# Copy base requirements (always needed)
COPY requirements/base.txt requirements/base.txt

# Copy environment-specific requirements
COPY requirements/${ENVIRONMENT}.txt requirements/${ENVIRONMENT}.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements/base.txt && \
    pip install --no-cache-dir -r requirements/${ENVIRONMENT}.txt

# Copy project
COPY . /app/

# Command to keep container running
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]