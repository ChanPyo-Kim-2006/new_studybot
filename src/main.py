import os
import cv2
import numpy as np
import mediapipe as mp
import traceback
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.core.config import SECRET_KEY
from src.state import shared_camera_manager, shared_detector, initialize_shared_resources
from src.api import auth, parent, child, video

# --- 🔧 로깅 설정 ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")
logger.info("🔥 FastAPI 앱 시작됨")

# --- ✅ FastAPI 앱 생성 ---
app = FastAPI()

# --- ✅ 템플릿 설정 ---
templates = Jinja2Templates(directory=os.path.join("src", "templates"))

# --- ✅ 미들웨어 등록 ---
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="session_token"
)

# --- ✅ 정적 파일 제공 ---
app.mount("/static", StaticFiles(directory=os.path.join("src", "static")), name="static")

# --- ✅ 라우터 등록 ---
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(parent.router, prefix="/parent", tags=["parent"])
app.include_router(child.router, prefix="/child", tags=["child"])
app.include_router(video.router, prefix="/video", tags=["video"])

# --- ✅ 전역 예외 핸들러 ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("❌ 전역 예외 발생:")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류 발생. 콘솔 로그를 확인하세요."}
    )

# --- ✅ 메인 페이지 ---
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "video_feed_url": "/video/video_feed"
    })

# --- ✅ 로그아웃 ---
@app.api_route("/logout", methods=["GET", "POST"])
async def logout():
    response = JSONResponse(content={"success": True, "message": "로그아웃되었습니다."})
    response.delete_cookie("session_token")
    return response

# --- ✅ 앱 시작 시 리소스 초기화 ---
@app.on_event("startup")
async def startup_event():
    logger.info("✅ startup_event 진입")

    initialize_shared_resources()

    if shared_detector is None or not shared_detector.is_initialized:
        logger.warning("🚨 shared_detector 비정상 상태 또는 초기화 실패")
    else:
        logger.info("✅ shared_detector 정상 및 초기화 완료")

    try:
        if shared_camera_manager and shared_camera_manager.is_initialized:
            logger.info("✅ 카메라 매니저 이미 초기화됨.")
        elif shared_camera_manager:
            shared_camera_manager.initialize_camera()
            logger.info("✅ 카메라 초기화 완료")
    except Exception as e:
        logger.exception("❌ 카메라 초기화 실패:")

# --- ✅ 앱 종료 시 리소스 정리 ---
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("✅ shutdown_event 진입")

    if shared_camera_manager:
        shared_camera_manager.release()
        logger.info("✅ 카메라 리소스 해제 완료.")

    if shared_detector:
        if hasattr(shared_detector, 'close') and callable(shared_detector.close):
            shared_detector.close()
            logger.info("✅ ConcentrationDetector 리소스 해제 완료.")
        else:
            logger.warning("⚠️ ConcentrationDetector에 close() 메서드 없음. 자원 해제 불완전할 수 있음.")

    logger.info("✅ 앱 종료 작업 완료.")
