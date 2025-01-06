from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://advisors_user:advisorspassword@localhost:5432/advisors_db" 
    model_config = ConfigDict(env_file=".env")

settings = Settings()