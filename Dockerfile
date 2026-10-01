# Agentry Container Definition
# Provides runtime control layer, Web Command Center, and OpenAI reverse proxy
FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency specifications first for optimal layer caching
COPY pyproject.toml .

# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Copy application source code and datasets
COPY . .

# Expose ports:
# 8501: Streamlit Command Center
# 8787: OpenAI Reverse Proxy & REST API Gateway
# 8788: Model Context Protocol (MCP) Server
EXPOSE 8501 8787 8788

# Default command: launch interactive Streamlit web dashboard
CMD ["python", "run.py", "web"]
