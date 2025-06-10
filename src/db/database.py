import mysql.connector
from src.core.config import DB_CONFIG

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"데이터베이스 연결 오류: {str(e)}")
        raise