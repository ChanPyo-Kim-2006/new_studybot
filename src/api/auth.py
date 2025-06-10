from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
import jwt
from datetime import datetime, timedelta

from src.core.config import SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from src.core.security import verify_password, create_access_token
from src.db.database import get_db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(request: Request):
    """현재 로그인한 사용자 정보 확인"""
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증되지 않은 사용자입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        user_type: str = payload.get("type")
        if username is None or user_type is None:  # 수정된 부분
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 인증 정보입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {
            "sub": username,
            "type": user_type,
            "user_id": payload.get("user_id"),
            "parent_id": payload.get("parent_id"),
            "child_code": payload.get("child_code")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 만료되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """활성 사용자 확인"""
    if not current_user:
        raise HTTPException(status_code=400, detail="비활성화된 사용자입니다.")
    return current_user

@router.get("/check-session")
async def check_session(current_user: dict = Depends(get_current_user)):
    """세션 유효성 확인"""
    return {
        "valid": True,
        "user_type": current_user.get("type"),
        "username": current_user.get("sub")
    }

@router.get("/user-info")
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """현재 사용자 정보 조회"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        user_type = current_user.get("type")
        user_info = {"type": user_type}
        
        try:
            if user_type == "parent":
                cursor.execute("""
                    SELECT p.username, p.email, 
                           COUNT(pc.child_code) as children_count
                    FROM parents p
                    LEFT JOIN parent_child pc ON p.parent_id = pc.parent_id
                    WHERE p.parent_id = %s
                    GROUP BY p.parent_id
                """, (current_user.get("parent_id"),))
                
                parent_info = cursor.fetchone()
                if parent_info:
                    user_info.update(parent_info)
                    
            elif user_type == "child":
                cursor.execute("""
                    SELECT u.username, u.email,
                           f.region, f.school_name, f.child_code
                    FROM users u
                    JOIN face_landmarks f ON u.user_id = f.user_id
                    WHERE u.user_id = %s
                """, (current_user.get("user_id"),))
                
                child_info = cursor.fetchone()
                if child_info:
                    user_info.update(child_info)
            
            return user_info
            
        finally:
            cursor.close()
            db.close()
            
    except Exception as e:
        print(f"사용자 정보 조회 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 정보를 조회하는 중 오류가 발생했습니다."
        )

@router.post("/refresh-token")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """토큰 갱신"""
    try:
        # 새로운 토큰 생성
        new_token = create_access_token(data={
            "sub": current_user["sub"],
            "type": current_user["type"],
            "user_id": current_user.get("user_id"),
            "parent_id": current_user.get("parent_id"),
            "child_code": current_user.get("child_code")
        })
        
        response = JSONResponse(content={"success": True, "message": "토큰이 갱신되었습니다."})
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=1800  # 30분
        )
        return response
        
    except Exception as e:
        print(f"토큰 갱신 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="토큰을 갱신하는 중 오류가 발생했습니다."
        )

@router.get("/permissions")
async def get_permissions(current_user: dict = Depends(get_current_user)):
    """사용자 권한 조회"""
    try:
        user_type = current_user.get("type")
        permissions = {
            "can_view_dashboard": False,
            "can_add_child": False,
            "can_view_child_status": False,
            "can_use_camera": False
        }
        
        if user_type == "parent":
            permissions.update({
                "can_view_dashboard": True,
                "can_add_child": True,
                "can_view_child_status": True
            })
        elif user_type == "child":
            permissions.update({
                "can_use_camera": True
            })
            
        return permissions
        
    except Exception as e:
        print(f"권한 조회 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="권한을 조회하는 중 오류가 발생했습니다."
        )

@router.get("/validate-token")
async def validate_token(token: str):
    """토큰 유효성 검증"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return {
            "valid": True,
            "user_type": payload.get("type"),
            "username": payload.get("sub"),
            "expires_at": datetime.fromtimestamp(payload.get("exp")).isoformat()
        }
    except jwt.ExpiredSignatureError:
        return {"valid": False, "error": "만료된 토큰입니다."}
    except jwt.JWTError:
        return {"valid": False, "error": "유효하지 않은 토큰입니다."}