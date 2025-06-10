from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from datetime import datetime
import json
import cv2
import secrets
import string
import numpy as np
import mysql.connector
import mediapipe as mp

from src.core.security import create_access_token, get_current_user
from src.core.config import DB_CONFIG
from src.db.database import get_db
from src.core.camera import CameraManager
from src.models.detector import ConcentrationDetector


router = APIRouter()
templates = Jinja2Templates(directory="src/templates")
detector = ConcentrationDetector()

camera_manager = CameraManager()
detector = ConcentrationDetector()


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def extract_face_landmarks(frame):
    mp_face_mesh = mp.solutions.face_mesh
    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=False) as face_mesh:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            points = []
            for landmark in landmarks.landmark:
                points.append([landmark.x, landmark.y, landmark.z])
            return np.array(points)

    return None

def compare_landmarks(db_landmarks, input_landmarks):
    if input_landmarks is None:
        return False

    if db_landmarks.shape != input_landmarks.shape:
        return False

    db_landmarks -= db_landmarks.mean(axis=0)
    input_landmarks -= input_landmarks.mean(axis=0)
    distance = np.linalg.norm(db_landmarks - input_landmarks)
    print(f"[DEBUG] 평균 거리: {distance:.4f}")
    return distance < 3.0

def verify_face(username: str, input_frame) -> bool:
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute("SELECT user_id, username FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if not user:
                print(f"사용자 정보 없음: username={username}")
                return False

            print(f"사용자 정보 찾음: user_id={user['user_id']}, username={user['username']}")

            cursor.execute("""
                SELECT landmarks 
                FROM face_landmarks 
                WHERE user_id = %s AND is_active = TRUE
            """, (user['user_id'],))

            result = cursor.fetchone()

            if result:
                print(f"얼굴 데이터 찾음: user_id={user['user_id']}")
                db_landmarks = np.array(json.loads(result['landmarks']))

                input_landmarks = extract_face_landmarks(input_frame)

                if input_landmarks is None:
                    print("⚠️ 입력 프레임에서 얼굴 인식 실패")
                    return False

                print(f"[DEBUG] DB shape: {db_landmarks.shape}, Input shape: {input_landmarks.shape}")

                if compare_landmarks(db_landmarks, input_landmarks):
                    return True

            print(f"얼굴 인증 실패: user_id={user['user_id']}")
            return False

        finally:
            cursor.close()
            db.close()

    except Exception as e:
        print(f"얼굴 검증 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

@router.post("/register")
async def register(request: Request):
    try:
        print("=== 얼굴 등록 시작 ===")
        data = await request.json()
        username = data.get("username")
        email = data.get("email")
        region = data.get("region")
        school_name = data.get("school_name")

        if not all([username, email, region, school_name]):
            missing = [k for k, v in zip(["사용자 이름", "이메일", "지역", "학교명"], [username, email, region, school_name]) if not v]
            return JSONResponse(content={"success": False, "message": f"다음 정보가 필요합니다: {', '.join(missing)}"}, status_code=400)

        camera = camera_manager.get_camera()
        if camera is None or not camera.isOpened():
            return JSONResponse(content={"success": False, "message": "카메라를 초기화할 수 없습니다."}, status_code=500)

        success, frame = camera.read()
        if not success:
            return JSONResponse(content={"success": False, "message": "카메라에서 이미지를 읽을 수 없습니다."}, status_code=500)

        frame = cv2.resize(frame, (640, 480))
        frame = cv2.flip(frame, 1)

        landmarks = extract_face_landmarks(frame)

        if landmarks is None:
            return JSONResponse(content={"success": False, "message": "얼굴을 감지할 수 없습니다."}, status_code=400)

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT u.user_id, u.username, u.email, f.region, f.school_name
            FROM users u
            LEFT JOIN face_landmarks f ON u.user_id = f.user_id
            WHERE u.username = %s OR u.email = %s
        """, (username, email))
        if cursor.fetchone():
            return JSONResponse(content={"success": False, "message": "이미 등록된 사용자입니다."}, status_code=400)

        child_code = f"STU-{secrets.token_hex(2)}-{secrets.token_hex(2)}"

        cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
        user_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO face_landmarks (user_id, landmarks, child_code, region, school_name)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, json.dumps(landmarks.tolist()), child_code, region, school_name))

        db.commit()

        access_token = create_access_token({"sub": username, "type": "child", "user_id": user_id})
        response = JSONResponse(content={"success": True, "child_code": child_code})
        response.set_cookie(key="session_token", value=access_token, httponly=True, max_age=1800)
        return response

    except Exception as e:
        print("등록 오류:", str(e))
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)

@router.post("/login")
async def login(request: Request):
    try:
        data = await request.json()
        username = data.get("username")

        camera = camera_manager.get_camera()
        if camera is None or not camera.isOpened():
            return JSONResponse(content={"success": False, "message": "카메라 초기화 실패"}, status_code=500)

        success, frame = camera.read()
        if not success:
            return JSONResponse(content={"success": False, "message": "카메라 프레임 읽기 실패"}, status_code=500)

        frame = cv2.resize(frame, (640, 480))
        frame = cv2.flip(frame, 1)

        if verify_face(username, frame):
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("""
                SELECT u.user_id, u.username, f.child_code
                FROM users u 
                JOIN face_landmarks f ON u.user_id = f.user_id 
                WHERE u.username = %s AND f.is_active = TRUE
            """, (username,))
            user = cursor.fetchone()
            access_token = create_access_token({"sub": username, "type": "child", "user_id": user["user_id"], "child_code": user["child_code"]})
            response = JSONResponse(content={"success": True})
            response.set_cookie(key="session_token", value=access_token, httponly=True, max_age=1800)
            return response
        else:
            return JSONResponse(content={"success": False, "message": "얼굴 인증 실패"}, status_code=401)

    except Exception as e:
        print("로그인 오류:", str(e))
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"success": False, "message": str(e)}, status_code=500)

@router.get("/main")
async def main_page(request: Request):
    current_user = await get_current_user(request)
    timestamp = datetime.now().timestamp()
    return templates.TemplateResponse("main.html", {
        "request": request,
        "username": current_user["sub"],
        "video_feed_url": f"/video/video_feed?t={timestamp}"
    })

@router.get("/status")
async def get_status(request: Request):
    try:
        current_status = detector.get_current_status()
        response_data = {
            "success": True,
            "status": current_status.get("status", "Unknown"),
            "concentration_score": current_status.get("concentration_score", 0),
            "gaze_status": current_status.get("gaze_status", "Unknown"),
            "face_detected": current_status.get("face_detected", False)
        }
        return JSONResponse(content=response_data)

    except Exception as e:
        print(f"상태 확인 오류: {str(e)}")
        return JSONResponse(
            content={
                "success": False,
                "message": "상태 확인 중 오류가 발생했습니다.",
                "error": str(e)
            },
            status_code=500
        )
