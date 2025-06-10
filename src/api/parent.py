from fastapi import APIRouter, Request, Depends, HTTPException, status, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse
from src.core.security import hash_password, verify_password, create_access_token
from src.core.config import DB_CONFIG, SECRET_KEY, JWT_ALGORITHM
from src.db.database import get_db
from datetime import datetime
from typing import Dict, Any
import jwt

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")

STATUS_TRANSLATION = {
    "No image": "이미지 없음",
    "Not focusing": "집중하지 않음",
    "Focusing": "집중",
    "Partially focusing": "부분 집중",
    "Face not detected": "얼굴 감지 안됨",
    "Eyes closed": "눈 감음",
    "Looking left": "왼쪽 응시",
    "Looking right": "오른쪽 응시"
}

def raise_unauthenticated():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

def raise_forbidden():
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="부모 계정만 접근 가능합니다.")

def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise_unauthenticated()
    except jwt.JWTError:
        raise_unauthenticated()

async def get_current_user(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        raise_unauthenticated()
    return decode_token(token)

@router.get("/register")
async def parent_register_page(request: Request):
    return templates.TemplateResponse("parent_register.html", {"request": request})

@router.post("/register")
async def parent_register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    email: str = Form(...),
    child_code: str = Form(...)
):
    if password != password_confirm:
        return templates.TemplateResponse("parent_register.html", {"request": request, "error": "비밀번호가 일치하지 않습니다."})

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT username FROM parents WHERE username = %s", (username,))
        if cursor.fetchone():
            return templates.TemplateResponse("parent_register.html", {"request": request, "error": "이미 사용 중인 아이디입니다."})

        cursor.execute("SELECT f.landmark_id FROM face_landmarks f WHERE f.child_code = %s AND f.is_active = TRUE", (child_code,))
        if not cursor.fetchone():
            return templates.TemplateResponse("parent_register.html", {"request": request, "error": "유효하지 않은 자녀 코드입니다."})

        hashed_pw = hash_password(password)
        cursor.execute("INSERT INTO parents (username, password, email) VALUES (%s, %s, %s)", (username, hashed_pw, email))
        parent_id = cursor.lastrowid
        cursor.execute("INSERT INTO parent_child (parent_id, child_code) VALUES (%s, %s)", (parent_id, child_code))
        db.commit()
        return RedirectResponse(url="/parent/login", status_code=303)
    except Exception as e:
        db.rollback()
        print(f"회원가입 오류: {e}")
        return templates.TemplateResponse("parent_register.html", {"request": request, "error": "회원가입 중 오류 발생."})
    finally:
        cursor.close()
        db.close()

@router.get("/login")
async def parent_login_page(request: Request):
    return templates.TemplateResponse("parent_login.html", {"request": request})

@router.post("/login")
async def parent_login(request: Request, username: str = Form(...), password: str = Form(...)):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT parent_id, password FROM parents WHERE username = %s", (username,))
        parent = cursor.fetchone()

        if not parent or not verify_password(password, parent["password"]):
            return templates.TemplateResponse("parent_login.html", {"request": request, "error": "아이디 또는 비밀번호가 일치하지 않습니다."})

        access_token = create_access_token(data={"sub": username, "type": "parent", "parent_id": parent["parent_id"]})
        response = RedirectResponse(url="/parent/dashboard", status_code=303)
        response.set_cookie("session_token", access_token, httponly=True, secure=True, samesite="lax", max_age=1800)
        return response
    finally:
        cursor.close()
        db.close()

@router.get("/dashboard")
async def parent_dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    if current_user.get("type") != "parent":
        raise_forbidden()

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT u.username, u.email, pc.child_code, f.region, f.school_name
            FROM parent_child pc
            JOIN face_landmarks f ON pc.child_code = f.child_code
            JOIN users u ON f.user_id = u.user_id
            WHERE pc.parent_id = %s
        """, (current_user["parent_id"],))

        children = cursor.fetchall()
        return templates.TemplateResponse("parent_dashboard.html", {"request": request, "username": current_user["sub"], "children": children})
    finally:
        cursor.close()
        db.close()

@router.post("/add-child")
async def add_child(request: Request, current_user: dict = Depends(get_current_user)):
    if current_user.get("type") != "parent":
        raise_forbidden()

    try:
        data = await request.json()
        child_code = data.get("child_code")

        db = get_db()
        cursor = db.cursor(dictionary=True)
        try:
            cursor.execute("SELECT landmark_id FROM face_landmarks WHERE child_code = %s AND is_active = TRUE", (child_code,))
            if not cursor.fetchone():
                return JSONResponse(content={"success": False, "message": "유효하지 않은 자녀 코드입니다."})

            cursor.execute("SELECT * FROM parent_child WHERE parent_id = %s AND child_code = %s", (current_user["parent_id"], child_code))
            if cursor.fetchone():
                return JSONResponse(content={"success": False, "message": "이미 등록된 자녀입니다."})

            cursor.execute("INSERT INTO parent_child (parent_id, child_code) VALUES (%s, %s)", (current_user["parent_id"], child_code))
            db.commit()
            return JSONResponse(content={"success": True})
        finally:
            cursor.close()
            db.close()
    except Exception as e:
        print(f"자녀 추가 오류: {e}")
        return JSONResponse(content={"success": False, "message": "자녀 추가 중 오류 발생"})

@router.get("/child_status/{child_code}")
async def get_child_status(request: Request, child_code: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("type") != "parent":
        raise_forbidden()

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT u.username AS child_name, fl.region, fl.school_name FROM users u JOIN face_landmarks fl ON u.user_id = fl.user_id WHERE fl.child_code = %s", (child_code,))
        child = cursor.fetchone()
        if not child:
            raise HTTPException(status_code=404, detail="해당 자녀 정보를 찾을 수 없습니다.")

        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return templates.TemplateResponse("child_status.html", {
                "request": request,
                "child_code": child_code,
                "child_name": child["child_name"],
                "region": child["region"],
                "school_name": child["school_name"],
                "video_feed_url": f"/video/video_feed?t={datetime.now().timestamp()}"
            })
        else:
            from src.state import shared_detector
            status_data = shared_detector.get_current_status()
            return JSONResponse(content={
                "success": True,
                "child_code": child_code,
                "child_name": child["child_name"],
                "status": STATUS_TRANSLATION.get(status_data.get("status"), "알 수 없음"),
                "concentration_score": status_data.get("concentration_score", 0),
                "gaze_status": STATUS_TRANSLATION.get(status_data.get("gaze_status"), "알 수 없음"),
                "face_detected": status_data.get("face_detected", False),
                "timestamp": datetime.now().isoformat()
            })
    finally:
        cursor.close()
        db.close()
