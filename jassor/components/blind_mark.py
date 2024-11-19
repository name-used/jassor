import cv2
import numpy as np
from scipy.fftpack import dct, idct


class Marker:
    def __init__(self, width: int, height: int, u: np.ndarray = None, v: np.ndarray = None):
        self.width = width
        self.height = height
        self.u = u if u is not None else np.linalg.qr(np.random.randn(height, height))[0].astype(np.float32)
        self.v = v if v is not None else np.linalg.qr(np.random.randn(width, width))[0].astype(np.float32)
        self.data = None
        self.cache_dct = None

    def image(self, image: np.ndarray):
        self.data = cv2.resize(image, (self.width, self.height))
        return self

    def mark(self, mark: np.ndarray):
        self.data = mark
        return self

    def item(self) -> np.ndarray:
        return self.data

    def map(self):
        if self.data is not None:
            self.data = np.tan((self.data - 0.5) * np.pi)
        return self

    def imap(self):
        if self.data is not None:
            self.data = np.arctan(self.data) / np.pi + 0.5
        return self

    def cross(self):
        if self.data is not None:
            self.data = self.u @ self.data @ self.v
        return self

    def icross(self):
        if self.data is not None:
            self.data = self.u.T @ self.data @ self.v.T
        return self

    def dct(self, k: int = 8, t: int = 0):
        if self.data is not None:
            self.cache_dct = {}
            # 对每个块进行 DCT 变换, 变换中留存主值
            dct_matrix = np.zeros_like(self.data)
            for i in range(0, self.height - k + 1, k):
                for j in range(0, self.width - k + 1, k):
                    block = self.data[i:i + k, j:j + k]
                    block = dct(dct(block.T, norm='ortho').T, norm='ortho')
                    if t > 0:
                        self.cache_dct[(i, j)] = block[:t, :t].copy()
                        # block[:t, :t] = 0
                    dct_matrix[i:i + k, j:j + k] = block
            self.data = dct_matrix
        return self

    def idct(self, k: int = 8, t: int = 0):
        if self.data is not None:
            # 对每个块进行 DCT 变换, 变换中留存主值
            idct_matrix = np.zeros_like(self.data)
            for i in range(0, self.height - k + 1, k):
                for j in range(0, self.width - k + 1, k):
                    block = self.data[i:i + k, j:j + k]
                    if t > 0:
                        block[:t, :t] = self.cache_dct[(i, j)]
                    block = idct(idct(block.T, norm='ortho').T, norm='ortho')
                    idct_matrix[i:i + k, j:j + k] = block
            self.data = idct_matrix
        return self
