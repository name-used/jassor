from scipy import signal
import cv2
import numpy as np


def process(image: np.ndarray, alpha: float = 1., s1: int = 9, s2: int = 5):
    # 过滤非黑白灰区域，适用于显微镜图
    # unify image channels to 3
    if len(image.shape) == 2:
        image = image[:, :, None]
    if image.shape[2] == 1:
        image = np.repeat(image, 3, axis=2)
    elif image.shape[2] == 4:
        image = image[:, :, 0: 3]
    # 计算结构蒙版
    m1 = np.max(image, 2)
    m2 = np.min(image, 2)
    m3 = m2 / 255 * (255-m1)
    m4 = np.clip(m3, 1, 8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (s1, s1))
    m5 = signal.convolve2d(m4, k, mode='same') / k.sum()
    mask = ((m1 - m2) / (m5 * alpha + 1e-19))
    mask = mask.clip(0, 1)
    mask = (mask * 255).round().astype(np.uint8)
    # 捕获边缘
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (s2, s2))
    cv2.dilate(mask, k, dst=mask, iterations=1)
    cv2.erode(mask, k, dst=mask, iterations=2)
    cv2.dilate(mask, k, dst=mask, iterations=1)

    return mask
