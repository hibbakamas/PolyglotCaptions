FROM python:3.11-slim   # Debian 12

WORKDIR /app

# -------------------------------------------------------
# Install ODBC dependencies
# -------------------------------------------------------
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
# Add Microsoft repo for Debian 12 (REQUIRED FOR ODBC 18)
# -------------------------------------------------------
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor \
    | tee /usr/share/keyrings/microsoft-prod.gpg > /dev/null

RUN echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] \
    https://packages.microsoft.com/debian/12/prod/ stable main" \
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
# Run API
# -------------------------------------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
