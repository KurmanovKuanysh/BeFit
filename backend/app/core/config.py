from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "befit"

    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 60)

    class Config:
        env_file = ".env"


settings = Settings()