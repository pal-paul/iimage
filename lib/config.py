"""
Configuration management for the object detection library using Pydantic.
"""

from typing import Set

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Model settings
    model_name: str = Field(default="yolov8n.pt", description="YOLO model name")
    confidence_threshold: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="Confidence threshold for detections"
    )
    iou_threshold: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="IoU threshold for NMS"
    )
    
    # File upload settings
    max_file_size: int = Field(
        default=10485760,
        gt=0,
        description="Maximum file size in bytes (10MB)"
    )
    allowed_extensions: str = Field(
        default="jpg,jpeg,png,bmp,webp",
        description="Comma-separated list of allowed file extensions"
    )
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server port")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    json_logs: bool = Field(default=True, description="Use JSON formatted logs")
    
    # Security settings
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    cors_origins: str = Field(default="*", description="CORS allowed origins")
    
    # Monitoring
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    
    # Application metadata
    app_name: str = Field(default="Image Object Detection API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment (development/staging/production)")
    
    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate model name format."""
        allowed_models = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"]
        if v not in allowed_models:
            raise ValueError(f"Model must be one of: {', '.join(allowed_models)}")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"Log level must be one of: {', '.join(allowed_levels)}")
        return v_upper
    
    def get_allowed_extensions_set(self) -> Set[str]:
        """Get allowed extensions as a set."""
        return set(ext.strip().lower() for ext in self.allowed_extensions.split(","))
    
    def get_cors_origins_list(self) -> list:
        """Get CORS origins as a list."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Create global settings instance
settings = Settings()

# Legacy compatibility
class Config:
    """Legacy config class for backward compatibility."""
    
    @property
    def MODEL_NAME(self) -> str:
        return settings.model_name
    
    @property
    def CONFIDENCE_THRESHOLD(self) -> float:
        return settings.confidence_threshold
    
    @property
    def IOU_THRESHOLD(self) -> float:
        return settings.iou_threshold
    
    @property
    def MAX_FILE_SIZE(self) -> int:
        return settings.max_file_size
    
    @property
    def ALLOWED_EXTENSIONS(self) -> Set[str]:
        return settings.get_allowed_extensions_set()
    
    @property
    def HOST(self) -> str:
        return settings.host
    
    @property
    def PORT(self) -> int:
        return settings.port
    
    @property
    def DEBUG(self) -> bool:
        return settings.debug


config = Config()
