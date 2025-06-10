from pydantic_settings import BaseSettings
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

class DatabaseSettings(BaseModel):
    host: str = os.getenv('DB_HOST', 'localhost')
    user: str = os.getenv('DB_USER', 'root')
    password: str = os.getenv('DB_PASSWORD', 'genii2024!')
    database: str = os.getenv('DB_NAME', 'studybot')

class Settings(BaseSettings):
    # API 설정
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '8000'))
    
    # 데이터베이스 설정
    db: DatabaseSettings = DatabaseSettings()
    
    # 얼굴 인식 모델 경로
    face_landmark_model: str = os.getenv('FACE_LANDMARK_MODEL', 'shape_predictor_68_face_landmarks.dat')
    
    # JWT 설정
    secret_key: str = os.getenv('SECRET_KEY', 'your-secret-key')
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    
    class Config:
        env_file = ".env"

# 설정 인스턴스 생성
settings = Settings()

# 기존 형식과의 호환성을 위한 변수들
DB_CONFIG = {
    'host': settings.db.host,
    'user': settings.db.user,
    'password': settings.db.password,
    'database': settings.db.database
}

FACE_LANDMARK_MODEL = settings.face_landmark_model
SECRET_KEY = settings.secret_key
JWT_ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes