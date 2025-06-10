import numpy as np
import cv2
import logging

logger = logging.getLogger("frame_utils")

def is_valid_frame(frame: np.ndarray) -> bool:
    """
    주어진 객체가 유효한 OpenCV 이미지 프레임인지 확인합니다.
    
    조건:
    - None이 아님
    - numpy.ndarray 타입
    - 비어 있지 않음
    - 3차원 배열 (H, W, C)
    - 채널 수는 3 (RGB/BGR) 또는 4 (RGBA/BGRA)
    """
    if frame is None:
        logger.debug("is_valid_frame: Frame is None.")
        return False

    if not isinstance(frame, np.ndarray):
        logger.debug(f"is_valid_frame: Frame is not a numpy array. Type: {type(frame)}")
        return False

    if frame.size == 0:
        logger.debug("is_valid_frame: Frame is empty (size == 0).")
        return False

    if frame.ndim != 3:
        logger.debug(f"is_valid_frame: Frame does not have 3 dimensions. ndim == {frame.ndim}")
        return False

    if frame.shape[2] not in (3, 4):
        logger.debug(f"is_valid_frame: Unexpected number of channels: {frame.shape[2]}")
        return False

    return True
