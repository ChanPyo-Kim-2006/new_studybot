import secrets
import base64

# 32바이트(256비트) 랜덤 키 생성
secret_key = secrets.token_bytes(32)
# base64로 인코딩하여 문자열로 변환
secret_key_str = base64.b64encode(secret_key).decode('utf-8')
print(secret_key_str)