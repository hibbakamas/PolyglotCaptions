FROM python:3.11-slim

WORKDIR /app

# -------------------------------------------------------
# Install system dependencies including ODBC driver for pyodbc
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
# Add Microsoft package repo for ODBC Driver 18 (Debian 12)
# -------------------------------------------------------
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor \
    | tee /usr/share/keyrings/microsoft-prod.gpg > /dev/null

RUN echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/config/debian/12/prod.list /" \
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
