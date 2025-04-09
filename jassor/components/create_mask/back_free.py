import numpy as np
import cv2
from numpy.lib.stride_tricks import sliding_window_view
from scipy.ndimage import uniform_filter


def process(image: np.ndarray, s: int = 3, std_thresh: float = 5., b: int = 13, k: int = 17):
    # 手动扩圈
    image = np.pad(image, [(1, 1), (1, 1), (0, 0)])
    image[0, :, :] = image[1, :, :]
    image[-1, :, :] = image[-2, :, :]
    image[:, 0, :] = image[:, 1, :]
    image[:, -1, :] = image[:, -2, :]
    # 在局部计算 std
    patches = sliding_window_view(image, (s, s, 1))
    patches = patches.std(axis=(3, 4, 5))    # 然后在 channel 上对 std 求平均
    mask = patches.mean(axis=2)
    # 再然后均值滤波扩散
    mask = uniform_filter(mask, size=(b, b))
    mask = uniform_filter(mask, size=(b, b))
    mask = uniform_filter(mask, size=(b, b))
    # 再阈值截断二值化
    mask = (mask > std_thresh).astype(np.uint8)
    # 最后做一个腐蚀膨胀
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    mask = cv2.dilate(mask, k, dst=mask, iterations=1)
    mask = cv2.erode(mask, k, dst=mask, iterations=2)
    mask = cv2.dilate(mask, k, dst=mask, iterations=1)
    return mask
