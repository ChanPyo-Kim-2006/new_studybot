from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import traceback

# .env 경로 강제 지정
env_path = os.path.join(os.path.dirname(__file__), '../../.env')
load_dotenv(dotenv_path=env_path)

class DatabaseSettings(BaseModel):
    host: str = os.getenv('DB_HOST', 'localhost')
    user: str = os.getenv('DB_USER', 'root')
    password: str = os.getenv('DB_PASSWORD', '')
    database: str = os.getenv('DB_NAME', 'studybot')

class Settings(BaseSettings):
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    db: DatabaseSettings = DatabaseSettings()
    secret_key: str = os.getenv('SECRET_KEY', 'your-secret-key')
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

    class Config:
        env_file = env_path

try:
    settings = Settings()
except Exception as e:
    print("❌ Settings 초기화 중 오류 발생:")
    traceback.print_exc()
    raise
