import cv2
import numpy as np
import mediapipe as mp
import traceback

from .gaze_tracker import GazeTracker
from utils.frame_utils import is_valid_frame


class ConcentrationDetector:
    def __init__(self):
        print("[INIT] ConcentrationDetector 초기화 시작")
        self.is_initialized = False

        try:
            # MediaPipe Face Detection 초기화
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_drawing = mp.solutions.drawing_utils

            self.face_detection = self.mp_face_detection.FaceDetection(
                min_detection_confidence=0.3,
                model_selection=0
            )
            print("[INFO] FaceDetection 초기화 완료")

            # GazeTracker 초기화 (GPU 환경이 아닐 경우 refine=False)
            self.gaze_tracker = GazeTracker(refine=False)
            if not self.gaze_tracker.is_initialized:
                raise RuntimeError("GazeTracker 초기화 실패")
            print("[INFO] GazeTracker 초기화 완료")

            self.current_frame = None
            self.current_status = {
                "status": "Not focusing",
                "concentration_score": 0,
                "gaze_status": "Face not detected",
                "face_detected": False
            }

            self.is_initialized = True
            print("[SUCCESS] ConcentrationDetector 초기화 완료")

        except Exception as e:
            print(f"[ERROR] ConcentrationDetector 초기화 중 오류 발생: {e}")
            traceback.print_exc()

    def get_current_status(self):
        return self.current_status

    def process_image(self, frame):
        if not self.is_initialized:
            return self._error_status("System Error: Not Initialized")

        if not is_valid_frame(frame):
            return self._error_status("Invalid image")

        try:
            self.current_frame = frame
            debug_image = frame.copy()
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_results = self.face_detection.process(frame_rgb)
            if not face_results.detections:
                return self._error_status("Face not detected")

            for detection in face_results.detections:
                self.mp_drawing.draw_detection(debug_image, detection)

            gaze_status = self.gaze_tracker.get_gaze(frame)
            debug_image = self.gaze_tracker.draw_debug(debug_image)

            result = self.analyze_concentration(
                face_detected=True,
                gaze_status=gaze_status
            )
            result["debug_image"] = debug_image
            self.current_status = result
            return result

        except Exception as e:
            print(f"[ERROR] 이미지 처리 중 예외 발생: {e}")
            traceback.print_exc()
            return self._error_status("System Error: Processing Failed")

    def _error_status(self, msg):
        self.current_status = {
            "status": msg,
            "concentration_score": 0,
            "gaze_status": msg,
            "face_detected": False,
            "debug_image": np.zeros((480, 640, 3), dtype=np.uint8)
        }
        return self.current_status

    def analyze_concentration(self, face_detected, gaze_status):
        score = 0
        status = "Not focusing"

        if face_detected:
            score += 20

        if gaze_status == "Focusing":
            score += 40
        elif gaze_status == "Eyes closed":
            score -= 20
        elif gaze_status in [
            "Face not detected",
            "Initialization error",
            "Processing error",
            "Invalid frame"
        ]:
            score += 0
        else:
            score += 0  # Looking left/right

        if score >= 70:
            status = "Focusing"
        elif score >= 40:
            status = "Partially focusing"

        return {
            "status": status,
            "concentration_score": max(0, min(100, score)),
            "gaze_status": gaze_status,
            "face_detected": face_detected,
            "raw_score": score
        }
