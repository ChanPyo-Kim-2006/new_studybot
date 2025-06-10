# src/state.py

import logging
import traceback

from src.core.camera import CameraManager
from src.models.detector import ConcentrationDetector

logger = logging.getLogger("state")

# 전역 공유 인스턴스
shared_camera_manager: CameraManager = None
shared_detector: ConcentrationDetector = None

def initialize_shared_resources():
    """
    공유 리소스를 초기화합니다.
    - CameraManager
    - ConcentrationDetector
    이 함수는 FastAPI 앱의 startup 이벤트에서 호출되어야 합니다.
    """
    global shared_camera_manager, shared_detector

    # --- CameraManager 초기화 ---
    try:
        if shared_camera_manager is None:
            logger.info("🔧 CameraManager 초기화 시작...")
            shared_camera_manager = CameraManager(device_index=0)
            logger.info("✅ CameraManager 인스턴스 생성 완료.")
        else:
            logger.info("ℹ️ CameraManager 이미 존재함.")
    except Exception as e:
        logger.exception("❌ CameraManager 초기화 중 예외 발생:")
        shared_camera_manager = None

    # --- ConcentrationDetector 초기화 ---
    try:
        if shared_detector is None:
            logger.info("🔧 ConcentrationDetector 초기화 시작...")
            shared_detector = ConcentrationDetector()
            if shared_detector.is_initialized:
                logger.info("✅ ConcentrationDetector 초기화 완료.")
            else:
                logger.warning("⚠️ ConcentrationDetector 초기화 실패: is_initialized=False")
        else:
            logger.info("ℹ️ ConcentrationDetector 이미 존재함.")
    except Exception as e:
        logger.exception("❌ ConcentrationDetector 초기화 중 예외 발생:")
        shared_detector = None
