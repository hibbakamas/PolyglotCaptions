FROM python:3.11-slim

WORKDIR /app

# -------------------------------------------------------
# Install system dependencies including ODBC driver for pyodbc
# -------------------------------------------------------
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg \
    unixodbc \
    unixodbc-dev \
    build-essential \
    ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Add Microsoft package repo for ODBC Driver 18
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/12/prod.list \
        > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql18

# -------------------------------------------------------
# Install Python dependencies
# -------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------
# Copy app source code
# -------------------------------------------------------
COPY . .

# -------------------------------------------------------
# Launch FastAPI with uvicorn
# -------------------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
