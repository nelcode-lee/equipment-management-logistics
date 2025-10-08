"""
Configuration management for the Equipment Tracking System
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # =============================================================================
    # API KEYS & EXTERNAL SERVICES
    # =============================================================================
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")
    
    # =============================================================================
    # DATABASE CONFIGURATION
    # =============================================================================
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./equipment_tracker.db")
    
    # =============================================================================
    # AWS S3 CONFIGURATION
    # =============================================================================
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "equipment-tracker-images")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # =============================================================================
    # REDIS CONFIGURATION
    # =============================================================================
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    APP_NAME: str = os.getenv("APP_NAME", "Equipment Management Logistics")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    
    # =============================================================================
    # EQUIPMENT MANAGEMENT SETTINGS
    # =============================================================================
    DEFAULT_THRESHOLD: int = int(os.getenv("DEFAULT_THRESHOLD", "20"))
    HIGH_PRIORITY_MULTIPLIER: float = float(os.getenv("HIGH_PRIORITY_MULTIPLIER", "1.5"))
    EQUIPMENT_TYPES: str = os.getenv("EQUIPMENT_TYPES", "Euro Pallet,Half Pallet,Blue Cage,Red Cage,Green Cage,White Cage")
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key_here")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:8000,https://equipment-office-dashboard.vercel.app,https://equipment-driver-app.vercel.app")
    
    # =============================================================================
    # LOGGING CONFIGURATION
    # =============================================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/equipment_tracker.log")
    
    # =============================================================================
    # EMAIL CONFIGURATION
    # =============================================================================
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@yourcompany.com")
    SUPPORT_EMAIL: str = os.getenv("SUPPORT_EMAIL", "support@yourcompany.com")
    
    # =============================================================================
    # FILE UPLOAD SETTINGS
    # =============================================================================
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_EXTENSIONS: str = os.getenv("ALLOWED_EXTENSIONS", "jpg,jpeg,png,gif,webp")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    
    # =============================================================================
    # MONITORING & ANALYTICS
    # =============================================================================
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    GOOGLE_ANALYTICS_ID: str = os.getenv("GOOGLE_ANALYTICS_ID", "")
    
    # =============================================================================
    # DEVELOPMENT SETTINGS
    # =============================================================================
    HOT_RELOAD: bool = os.getenv("HOT_RELOAD", "True").lower() == "true"
    ENABLE_DOCS: bool = os.getenv("ENABLE_DOCS", "True").lower() == "true"
    TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "sqlite:///./test_equipment_tracker.db")
    
    # =============================================================================
    # HELPER METHODS
    # =============================================================================
    def get_equipment_types_list(self) -> list:
        """Get equipment types as a list"""
        return [t.strip() for t in self.EQUIPMENT_TYPES.split(',') if t.strip()]
    
    def get_cors_origins_list(self) -> list:
        """Get CORS origins as a list"""
        return [o.strip() for o in self.CORS_ORIGINS.split(',') if o.strip()]
    
    def get_allowed_extensions_list(self) -> list:
        """Get allowed file extensions as a list"""
        return [e.strip().lower() for e in self.ALLOWED_EXTENSIONS.split(',') if e.strip()]

settings = Settings()

