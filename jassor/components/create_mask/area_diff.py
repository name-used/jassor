from scipy import signal
from scipy import ndimage
import cv2
import numpy as np


def process(image: np.ndarray, s: int = 9, score_thresh: float = 0.012):
    # 探测边缘（我也不知道为什么，但总之，它确实可以做到）
    # unify image channels to 3
    if len(image.shape) == 2:
        image = image[:, :, None]
    if image.shape[2] == 1:
        image = np.repeat(image, 3, axis=2)
    elif image.shape[2] == 4:
        image = image[:, :, 0: 3]
    image = image / 255
    diff: np.ndarray = np.zeros_like(image)
    # 中值滤波对均值滤波做差
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (s, s))
    for i in range(3):
        mean_filter = signal.convolve2d(image[..., i], k, mode='same') / k.sum()
        mid_filter = ndimage.median_filter(image[..., i], size=s, mode='reflect')
        diff[..., i] = abs(mean_filter - mid_filter)
    # 差主体低于 0.1 的视为背景板
    mask = diff.max(axis=2) / score_thresh
    # mask = diff.sum(axis=2) > score_thresh
    mask = mask.clip(0, 1)
    mask = (mask * 255).round().astype(np.uint8)

    return mask
