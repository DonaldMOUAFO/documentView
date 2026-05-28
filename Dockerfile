# =========================================================
# Base Image
# =========================================================
FROM python:3.12-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure logs appear immediately
ENV PYTHONUNBUFFERED=1

# Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# =========================================================
# Working Directory
# =========================================================
WORKDIR /documentview

# Streamlit configuration
ENV DATA_DIR=/documentview/data

# =========================================================
# Install system dependencies
# =========================================================
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# =========================================================
# Install Python dependencies first
# (better Docker layer caching)
# =========================================================
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# =========================================================
# Copy application source
# =========================================================
COPY . .

# =========================================================
# Install local package (if setup.py / pyproject.toml exists)
# =========================================================
RUN pip install --no-cache-dir .

# =========================================================
# Create non-root user
# =========================================================
# RUN useradd -m user

# USER user

# =========================================================
# Expose Streamlit port
# =========================================================
EXPOSE 8501

# =========================================================
# Healthcheck
# =========================================================
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# =========================================================
# Start application
# =========================================================
CMD ["streamlit", "run", "src/application/app.py", "--server.port=8501", "--server.address=0.0.0.0"]