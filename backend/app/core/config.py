from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "MediMind AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8080

    class Config:
        env_file = ".env"


settings = Settings()