# ANPTOP Backend Dockerfile - Core Edition
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# ============================================================================
# SYSTEM DEPENDENCIES
# ============================================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget git vim nano jq unzip zip tar gzip bzip2 xz-utils \
    ca-certificates \
    nmap masscan netcat-openbsd socat \
    smbclient smbmap rpcbind \
    snmp postgresql-client mariadb-client \
    sslscan docker.io awscli kubectl \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# PYTHON CORE PACKAGES
# ============================================================================
RUN pip install --no-cache-dir \
    dnspython \
    boto3 \
    azure-identity \
    azure-mgmt-resource \
    google-cloud \
    google-cloud-storage \
    google-cloud-secret-manager \
    scoutsuite \
    checkov \
    impacket \
    wfuzz \
    wpscan \
    web3 \
    stripe \
    loguru \
    aiofiles \
    aiohttp \
    aiosqlite \
    asyncpg \
    sqlalchemy \
    passlib \
    python-jose \
    pyotp \
    qrcode \
    pydantic \
    pydantic-settings \
    email-validator \
    pyyaml \
    tomli \
    uvicorn \
    fastapi \
    python-multipart \
    redis \
    minio \
    prometheus-client \
    pytest \
    pytest-asyncio \
    httpx \
    && rm -rf /root/.cache

# ============================================================================
# COPY APPLICATION CODE
COPY . .

# ============================================================================
# CREATE DIRECTORIES
RUN mkdir -p /data/evidence \
    && chown -R nobody:nogroup /data/evidence \
    && chmod -R 755 /data/evidence

# ============================================================================
# EXPOSE PORT
EXPOSE 8000

# ============================================================================
# HEALTH CHECK
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ============================================================================
# RUN THE APPLICATION
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
