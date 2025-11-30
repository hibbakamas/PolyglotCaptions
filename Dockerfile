# Base image: Debian 11 + Python 3.11
FROM python:3.11-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    build-essential \
    ffmpeg \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------
# Add Microsoft GPG key + repo for Debian 11
# -------------------------------------------------------
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list \
    > /etc/apt/sources.list.d/mssql-release.list

# -------------------------------------------------------
# Install MS ODBC 18 driver
# -------------------------------------------------------
RUN apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18

# -------------------------------------------------------
# Install Python dependencies
# -------------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------
# Copy app code
# -------------------------------------------------------
COPY . .

# -------------------------------------------------------
# Run the API
# -------------------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
