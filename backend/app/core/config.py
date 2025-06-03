import os
from typing import List, Union
from pydantic import AnyHttpUrl, validator, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    
    # PostgreSQL settings
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER", "172.30.98.213")
    POSTGRES_PORT: int = int(os.environ.get("POSTGRES_PORT", "5432"))
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "DoRadmin")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "1232")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "DoR")
    
    # Redis settings
    REDIS_SERVER: str = os.environ.get("REDIS_SERVER", "172.30.98.214")
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", "6379"))
    
    # Security settings
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "insecure_default_key_for_development_only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings - Allow all origins in development
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["*"]
    
    # Ollama API settings
    OLLAMA_API_URL: str = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
    
    # Database connection string - async
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Database connection string - sync
    @property
    def SQLALCHEMY_DATABASE_URI_SYNC(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis connection string
    @property
    def REDIS_DSN(self) -> str:
        return f"redis://{self.REDIS_SERVER}:{self.REDIS_PORT}/0"
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        validate_assignment = False
        extra = "ignore"  # This is key - ignore extra fields from .env file


settings = Settings()