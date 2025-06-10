import cv2
import numpy as np
import mediapipe as mp
from src.utils.frame_utils import is_valid_frame


class GazeTracker:
    def __init__(self, hist_size=10, ear_thresh=0.18, focus_lo=0.9, focus_hi=1.1):
        self.mesh = None
        self.hist_size = hist_size
        self.ear_thresh = ear_thresh
        self.focus_lo = focus_lo
        self.focus_hi = focus_hi
        self.gaze_hist = []
        self.is_initialized = True
        self.left_eye = [33, 159, 158, 133, 153, 144]
        self.right_eye = [362, 386, 385, 263, 373, 380]

    def _init_mesh(self):
        if self.mesh is not None:
            return
        print("[DEBUG] MediaPipe FaceMesh 초기화 중 (CPU 모드)...")
        self.mesh = mp.solutions.face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=False,
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        print("[DEBUG] MediaPipe FaceMesh 초기화 완료")

    def get_gaze(self, frame: np.ndarray) -> str:
        if not is_valid_frame(frame):
            print("WARN: GazeTracker - 유효하지 않은 프레임")
            return "Invalid frame"

        self._init_mesh()

        try:
            result = self.mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        except Exception as e:
            print(f"ERROR: MediaPipe 처리 중 오류: {e}")
            return "Processing error"

        if not hasattr(result, 'multi_face_landmarks') or not result.multi_face_landmarks:
            return "Face not detected"

        landmarks = result.multi_face_landmarks[0].landmark

        try:
            ear = np.mean([
                self._calculate_ear(landmarks, self.left_eye),
                self._calculate_ear(landmarks, self.right_eye)
            ])
        except ZeroDivisionError:
            return "Processing error"

        if ear < self.ear_thresh:
            return "Eyes closed"

        try:
            gaze_ratio = np.mean([
                self._calculate_gaze_ratio(frame, landmarks, self.left_eye),
                self._calculate_gaze_ratio(frame, landmarks, self.right_eye)
            ])
            gaze_ratio = np.clip(gaze_ratio, 0.1, 10.0)
        except Exception as e:
            print(f"ERROR: Gaze ratio 계산 중 오류: {e}")
            return "Processing error"

        self.gaze_hist.append(gaze_ratio)
        if len(self.gaze_hist) > self.hist_size:
            self.gaze_hist.pop(0)

        avg_ratio = float(np.mean(self.gaze_hist))
        if self.focus_lo < avg_ratio < self.focus_hi:
            return "Focusing"
        return "Looking left" if avg_ratio <= self.focus_lo else "Looking right"

    def draw_debug(self, frame: np.ndarray) -> np.ndarray:
        if not is_valid_frame(frame):
            return np.zeros((480, 640, 3), dtype=np.uint8)

        self._init_mesh()

        try:
            result = self.mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        except Exception as e:
            print(f"ERROR: draw_debug 처리 중 오류: {e}")
            return frame

        if not hasattr(result, 'multi_face_landmarks') or not result.multi_face_landmarks:
            return frame

        annotated = frame.copy()
        h, w = annotated.shape[:2]
        for idx in self.left_eye + self.right_eye:
            lm = result.multi_face_landmarks[0].landmark[idx]
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(annotated, (x, y), 2, (0, 255, 0), -1)
        return annotated

    @staticmethod
    def _calculate_ear(landmarks, eye_indices):
        pts = np.array([[landmarks[i].x, landmarks[i].y] for i in eye_indices])
        v1 = np.linalg.norm(pts[1] - pts[5])
        v2 = np.linalg.norm(pts[2] - pts[4])
        h = np.linalg.norm(pts[0] - pts[3])
        if h == 0:
            raise ZeroDivisionError("EAR 계산 중 나눗셈 오류")
        return (v1 + v2) / (2.0 * h)

    @staticmethod
    def _calculate_gaze_ratio(frame, landmarks, eye_indices):
        h, w = frame.shape[:2]
        pts = np.array([[landmarks[i].x * w, landmarks[i].y * h] for i in eye_indices], dtype=np.int32)
        min_pt = pts.min(axis=0) - 2
        max_pt = pts.max(axis=0) + 2
        x1 = max(0, int(min_pt[0]))
        y1 = max(0, int(min_pt[1]))
        x2 = min(w, int(max_pt[0]))
        y2 = min(h, int(max_pt[1]))
        if x2 <= x1 or y2 <= y1:
            return 1.0
        roi = frame[y1:y2, x1:x2]
        if roi.size == 0:
            return 1.0
        gray = cv2.equalizeHist(cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY))
        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,
            11, 2
        )
        mid = thresh.shape[1] // 2
        l_white = cv2.countNonZero(thresh[:, :mid])
        r_white = cv2.countNonZero(thresh[:, mid:])
        return 1.0 if (l_white + r_white) == 0 else l_white / (r_white + 1e-6)

    def close(self):
        if self.mesh:
            self.mesh.close()
            print("DEBUG: GazeTracker FaceMesh 리소스 해제 완료.")
        self.mesh = None
