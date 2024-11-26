from typing import Union, Optional
import cv2
import numpy as np
from scipy.fftpack import dct, idct


class Marker:
    def __init__(self, u: int, v: int):
        self.u = np.linalg.qr(np.random.randn(u, u))[0].astype(np.float32)
        self.v = np.linalg.qr(np.random.randn(v, v))[0].astype(np.float32)
        self.h = u
        self.w = v
        self.dct_image: Optional[np.ndarray] = None

    def map(self, image: np.ndarray):
        # image = (h, w):: float -> [0, 1]
        image = cv2.resize(image, (self.w, self.h))
        # [0, 1] ==>> (-∞, +∞)
        image = np.tan((image - 0.5) * np.pi * (1 - 1e-9))
        # dct 主值化
        k = 8
        t = 1
        # 对每个块进行 DCT 变换, 变换中留存主值
        self.dct_image = np.zeros_like(image)
        for i in range(0, self.h - k + 1, k):
            for j in range(0, self.w - k + 1, k):
                block = image[i:i + k, j:j + k]
                block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                self.dct_image[i:i + k, j:j + k] = block
        # 提取低频部分
        dct_image = self.dct_image[0::k, 0::k]
        # 对低频部分做交叉变换
        cross_image = self.u @ dct_image @ self.v
        # 变换结果即为信息加载画板
        return cross_image

    def imap(self, cross_image: np.ndarray):
        # cross_image = (h//8, w//8):: float -> (-∞, +∞)
        # 逆交叉变换得到低频部分
        dct_image = self.u.T @ cross_image @ self.v.T
        # 装包回 dct 图
        k = 8
        t = 1
        self.dct_image[0::k, 0::k] = dct_image
        # 对每个块进行 IDCT 变换, 获得原始信息图
        image = np.zeros_like(self.dct_image)
        for i in range(0, self.h - k + 1, k):
            for j in range(0, self.w - k + 1, k):
                block = self.dct_image[i:i + k, j:j + k]
                block = idct(idct(block.T, norm='ortho').T, norm='ortho')
                image[i:i + k, j:j + k] = block

        # 变换结果即为信息加载画板
        return cross_image
