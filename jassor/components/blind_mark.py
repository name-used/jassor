from typing import Union
import cv2
import numpy as np
from scipy.fftpack import dct, idct

k = 8


def map_to(img_in: np.ndarray):
    """
    将给定图像映射到目标域上
    :param img_in: uint8 图像
    :return: dct 图像
    """
    h, w = img_in.shape
    H = h + -h % k
    W = w + -w % k
    image = np.zeros(shape=(H, W), dtype=np.uint8)
    image[:h, :w] = img_in
    # 数据空间变换 [0, 255] -> [0.5, 255.5] -> (-1, 1) -> (-∞, +∞)
    image = (image.astype(np.float64) + 0.5 - 128) / 128
    image = np.tan(image * np.pi / 2)

    # 对每个块进行 DCT 变换, 变换中留存主值
    result = np.zeros_like(image, dtype=np.float32)
    for i in range(0, H, k):
        for j in range(0, W, k):
            block = image[i:i + k, j:j + k]
            block = dct(dct(block.T, norm='ortho').T, norm='ortho')
            # block = u @ block @ v
            result[i:i + k, j:j + k] = block
    return result


def imap_to(img_in: np.ndarray):
    """
    将给定目标域图像映射回 uint8
    :param img_in: dct 图像
    :return: uint8 图像
    """
    h, w = img_in.shape
    H = h + -h % k
    W = w + -w % k
    image = np.zeros(shape=(H, W), dtype=np.float32)
    image[:h, :w] = img_in
    result = np.zeros_like(image, dtype=np.float32)
    for i in range(0, H, k):
        for j in range(0, W, k):
            block = image[i:i + k, j:j + k]
            # block = u.T @ block @ v.T
            block = idct(idct(block.T, norm='ortho').T, norm='ortho')
            result[i:i + k, j:j + k] = block

    # 数据空间变换 [0, 255] -> [0.5, 255.5] -> (-1, 1) -> (-∞, +∞)
    result = np.arctan(result) * 2 / np.pi
    result = (result * 128 + 128).astype(np.uint8)
    return result

print('wwwwwwwwww')
