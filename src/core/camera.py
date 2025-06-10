import cv2
import time
import logging

logger = logging.getLogger("camera_manager")

class CameraManager:
    def __init__(self, device_index=0, backend=None, width=640, height=480, max_retries=3):
        self.device_index = device_index
        self.backend = backend
        self.width = width
        self.height = height
        self.max_retries = max_retries

        self.camera = None
        self.is_initialized = False

    def initialize_camera(self) -> bool:
        """
        카메라를 초기화하고, 테스트 프레임을 성공적으로 읽을 수 있을 경우에만 초기화 완료로 간주함.
        """
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"🔁 [카메라 초기화 시도] {attempt}/{self.max_retries}")

            try:
                self._open_camera()

                if not self.camera.isOpened():
                    logger.warning("❌ 카메라 열기 실패")
                    self._reset_camera()
                    time.sleep(1)
                    continue

                self._configure_resolution()

                if not self._test_read():
                    logger.warning("⚠️ 프레임 읽기 실패")
                    self._reset_camera()
                    time.sleep(1)
                    continue

                self.is_initialized = True
                logger.info("✅ 카메라 초기화 성공")
                return True

            except Exception as e:
                logger.exception(f"❗ 카메라 초기화 중 예외 발생: {e}")
                self._reset_camera()
                time.sleep(1)

        self.is_initialized = False
        raise RuntimeError("🚨 카메라 초기화 실패: 최대 재시도 초과")

    def _open_camera(self):
        if self.backend:
            self.camera = cv2.VideoCapture(self.device_index, self.backend)
        else:
            self.camera = cv2.VideoCapture(self.device_index)

    def _configure_resolution(self):
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

    def _test_read(self) -> bool:
        ret, frame = self.camera.read()
        return ret and frame is not None

    def _reset_camera(self):
        if self.camera:
            self.camera.release()
        self.camera = None
        self.is_initialized = False

    def get_camera(self):
        return self.camera

    def release(self):
        if self.camera:
            self.camera.release()
            logger.info("🧹 카메라 자원 해제 완료")
        self.camera = None
        self.is_initialized = False
