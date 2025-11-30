FROM python:3.11-bullseye   # Debian 11

WORKDIR /app

# -------------------------------------------------------
# Install system deps including ODBC + ffmpeg
# -------------------------------------------------------
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    build-essential \
    ffmpeg \
    apt-transport-https && \
    rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------
# Microsoft ODBC Driver 18 repo for Debian 11
# -------------------------------------------------------
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list \
    > /etc/apt/sources.list.d/mssql-release.list

# -------------------------------------------------------
# Install ODBC Driver 18
# -------------------------------------------------------
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

# -------------------------------------------------------
# Install Python deps
# -------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------
# Copy project
# -------------------------------------------------------
COPY . .

# -------------------------------------------------------
# Run API
# -------------------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
