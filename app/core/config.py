"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    environment: str = "development"
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key: str = "dev_api_key"
    
    # LLM Provider Selection (Cerebras is PRIMARY)
    llm_provider: str = "cerebras"
    
    # Cerebras Settings (PRIMARY PROVIDER - GPT-OSS-120B)
    cerebras_api_key: str = ""
    cerebras_model: str = "gpt-oss-120b"
    cerebras_base_url: str = "https://api.cerebras.ai/v1"
    
    # OpenRouter Settings (FALLBACK)
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/develop_health_mvp"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # ChromaDB
    chroma_persist_directory: str = "./chroma_db"
    
    # Neo4j Graph Database
    neo4j_host: str = "1d4d82ab.databases.neo4j.io"
    neo4j_port: int = 7687
    neo4j_uri: str = "neo4j+s://1d4d82ab.databases.neo4j.io"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    neo4j_database: str = "neo4j"
    
    # Paths
    pa_forms_output_dir: str = "/tmp/pa_forms"
    mock_data_dir: str = "./mock_data"
    
    # Logging
    log_level: str = "INFO"
    
    # LLM Settings
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1000
    llm_timeout: int = 30
    
    # Confidence Thresholds
    eligibility_confidence_threshold: float = 0.8
    quality_score_threshold: float = 0.9
    
    # Observability & Monitoring
    logfire_api_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"
    enable_monitoring: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


# Global settings instance
settings = Settings()
