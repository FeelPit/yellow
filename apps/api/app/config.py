from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    
    database_url: str = "postgresql://yellow:yellow123@localhost:5432/yellow_db"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 10080


settings = Settings()
