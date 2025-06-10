from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cv2
import time
from src.core.camera import CameraManager
from src.models.detector import ConcentrationDetector

router = APIRouter()

# 싱글톤처럼 사용할 전역 객체
camera_manager = CameraManager()
detector = ConcentrationDetector()


def generate_frames():
    """MJPEG 프레임 생성기"""
    retries = 0
    camera = camera_manager.get_camera()

    if camera is None:
        print("카메라 없음. 프레임 생성 중단.")
        return

    while True:
        try:
            success, frame = camera.read()
            if not success or frame is None or frame.size == 0:
                print("프레임 읽기 실패. 재시도 중...")
                retries += 1
                if retries >= 5:
                    print("프레임 재시도 초과. 카메라 재초기화 시도.")
                    camera.release()
                    camera_manager.initialize_camera()
                    camera = camera_manager.get_camera()
                    retries = 0
                    time.sleep(1)
                continue

            retries = 0
            frame = cv2.flip(frame, 1)
            result = detector.process_image(frame)
            debug_frame = result.get("debug_image", frame)

            ret, buffer = cv2.imencode('.jpg', debug_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            if not ret:
                continue

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        except Exception as e:
            print(f"프레임 처리 중 오류: {e}")
            time.sleep(1)
            continue


@router.get("/video_feed")
async def video_feed():
    """MJPEG 영상 스트리밍"""
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
