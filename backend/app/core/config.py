"""
ANPTOP Backend - Core Configuration
"""

from typing import List, Optional
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "ANPTOP"
    APP_VERSION: str = "2.0.0"
    APP_ENV: str = Field(default="development", env="APP_ENV")
    DEBUG: bool = Field(default=True, env="DEBUG")
    SECRET_KEY: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    
    # Database
    DATABASE_URL: str = Field(default="postgresql+asyncpg://anptop:anptop@localhost:5432/anptop", env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # JWT Authentication
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    JWT_SECRET_KEY: str = Field(default="jwt-secret-change-in-production", env="JWT_SECRET_KEY")
    JWT_REFRESH_SECRET_KEY: str = Field(default="jwt-refresh-secret-change-in-production", env="JWT_REFRESH_SECRET_KEY")
    
    # MFA Configuration
    MFA_ENABLED: bool = Field(default=True, env="MFA_ENABLED")
    MFA_ISSUER_NAME: str = Field(default="ANPTOP", env="MFA_ISSUER_NAME")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS",
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # n8n Configuration
    N8N_URL: str = Field(default="http://localhost:5678", env="N8N_URL")
    N8N_API_KEY: Optional[str] = Field(default=None, env="N8N_API_KEY")
    N8N_BASIC_AUTH_USER: Optional[str] = Field(default=None, env="N8N_BASIC_AUTH_USER")
    N8N_BASIC_AUTH_PASSWORD: Optional[str] = Field(default=None, env="N8N_BASIC_AUTH_PASSWORD")
    
    # Evidence Storage
    EVIDENCE_STORAGE_PATH: str = Field(default="/data/evidence", env="EVIDENCE_STORAGE_PATH")
    EVIDENCE_RETENTION_DAYS: int = Field(default=365, env="EVIDENCE_RETENTION_DAYS")
    
    # MinIO/S3 Configuration
    MINIO_ENDPOINT: Optional[str] = Field(default=None, env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: Optional[str] = Field(default=None, env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: Optional[str] = Field(default=None, env="MINIO_SECRET_KEY")
    MINIO_BUCKET: str = Field(default="anptop-evidence", env="MINIO_BUCKET")
    MINIO_SECURE: bool = Field(default=False, env="MINIO_SECURE")
    
    # Metasploit Configuration
    METASPLOIT_RPC_URL: Optional[str] = Field(default=None, env="METASPLOIT_RPC_URL")
    METASPLOIT_RPC_USER: Optional[str] = Field(default=None, env="METASPLOIT_RPC_USER")
    METASPLOIT_RPC_PASSWORD: Optional[str] = Field(default=None, env="METASPLOIT_RPC_PASSWORD")
    
    # OpenVAS Configuration
    OPENVAS_URL: Optional[str] = Field(default=None, env="OPENVAS_URL")
    OPENVAS_PORT: int = Field(default=9392, env="OPENVAS_PORT")
    OPENVAS_USER: Optional[str] = Field(default=None, env="OPENVAS_USER")
    OPENVAS_PASSWORD: Optional[str] = Field(default=None, env="OPENVAS_PASSWORD")
    
    # Nmap Configuration
    NMAP_PATH: str = Field(default="/usr/bin/nmap", env="NMAP_PATH")
    NMAP_ARGS: str = Field(default="-sV -sC --script=default", env="NMAP_ARGS")
    
    # Nuclei Configuration
    NUCLEI_PATH: str = Field(default="/usr/bin/nuclei", env="NUCLEI_PATH")
    NUCLEI_TEMPLATES_PATH: str = Field(default="/opt/nuclei-templates", env="NUCLEI_TEMPLATES_PATH")
    
    # Masscan Configuration
    MASSCAN_PATH: str = Field(default="/usr/bin/masscan", env="MASSCAN_PATH")
    MASSCAN_ARGS: str = Field(default="--rate=1000", env="MASSCAN_ARGS")
    
    # Security Settings
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, env="RATE_LIMIT_WINDOW")
    
    # File Upload
    MAX_FILE_SIZE: int = Field(default=104857600, env="MAX_FILE_SIZE")  # 100MB
    ALLOWED_FILE_TYPES: List[str] = Field(
        default=[
            "application/pdf",
            "image/png",
            "image/jpeg",
            "text/plain",
            "application/zip",
            "application/x-zip-compressed",
            "application/octet-stream",
        ],
        env="ALLOWED_FILE_TYPES",
    )
    
    # Reporting
    REPORT_TEMPLATE_PATH: str = Field(default="/templates/reports", env="REPORT_TEMPLATE_PATH")
    DEFAULT_REPORT_FORMAT: str = Field(default="pdf", env="DEFAULT_REPORT_FORMAT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
