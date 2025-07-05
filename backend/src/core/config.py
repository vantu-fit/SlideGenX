from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Add your configuration variables here
    DATABASE_URL: str = "sqlite:///./test.db"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "database"

    ALGORITHM: str = "HS256"
    SECRET_KEY: str = "your_secret_key"
    GEMINI_API_KEY: str = "your_gemini_api_key"

settings = Config()