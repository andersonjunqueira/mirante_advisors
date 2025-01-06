from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://advisors_user:advisorspassword@localhost:5432/advisors_db"
    class Config:
        env_file = ".env"

settings = Settings()