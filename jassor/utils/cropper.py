from typing import Tuple
import numpy as np
import cv2


def crop(image: np.ndarray, center: Tuple[float, float], size: Tuple[int, int], degree: float = 0, scale: float = 1, nearest: bool = True) -> np.ndarray:
    """
        切图函数，用于切割给定图像，参数含义如下所示：
        1. 定义一个尺寸为 size 的窗口
        2. 将窗口依 scale 倍数缩放（scale > 1 时窗口变大）
        3. 将窗口旋转 degree 角度（逆时针顺序）
        4. 将窗口中心平移至图像的 center 处
        5. 用窗口在 image 中切取数据，当 nearest 为真时，切取数据均来自 image 原图最近相关点，否则来自邻近点的线性运算
        6. 所采集点回归收拢至原窗口，形成一张尺寸为 size 的图像
        请注意：图像与矩阵的顺逆时针顺序相反，图像逆时针对应矩阵顺时针
    """
    if len(image.shape) == 2:
        return _crop(image, center, size, degree, scale, nearest)
    elif len(image.shape) == 3:
        results = [_crop(image[:, :, i], center, size, degree, scale, nearest) for i in range(image.shape[2])]
        return np.stack(results, axis=2)
    else:
        raise ValueError(f'Shape of image must be array[y, x] or array[y, x, c], but found {type(image)} - {image.shape}')


def _crop(image: np.ndarray, center: Tuple[float, float], size: Tuple[int, int], degree: float = 0, scale: float = 1, nearest: bool = True) -> np.ndarray:
    H, W = image.shape
    x_center, y_center = center
    w, h = map(int, (size, size) if isinstance(size, (int, float)) else size)
    wb = (w - 1) / 2
    hb = (h - 1) / 2
    r = degree * np.pi / 180
    sina, cosa = np.sin(r), np.cos(r)
    w1b = (wb * abs(cosa) + hb * abs(sina)) * scale
    h1b = (hb * abs(cosa) + wb * abs(sina)) * scale
    l1, u1 = round(x_center - w1b), round(y_center - h1b)
    r1, d1 = round(x_center + w1b), round(y_center + h1b)
    # get the img-array -> need to be implement
    img = image[max(0, u1): max(0, d1)+1, max(0, l1): max(0, r1)+1]
    img = np.pad(img, [[max(0, -u1), max(0, d1 - H + 1)], [max(0, -l1), max(0, r1 - W + 1)]])
    if nearest:
        # warp_affine -> https://blog.csdn.net/qq_40939814/article/details/117966835
        # build map-matrix
        x_grid, y_grid = np.meshgrid(np.arange(w), np.arange(h))
        x_grid = x_grid - wb
        y_grid = y_grid - hb
        x_index = ((cosa * x_grid + sina * y_grid) * scale + w1b).round().astype(np.int32)
        y_index = ((cosa * y_grid - sina * x_grid) * scale + h1b).round().astype(np.int32)
        # use the numpy-broadcast
        return img[
            np.clip(y_index, 0, d1 - u1),
            np.clip(x_index, 0, r1 - l1),
        ]
    else:
        ws = round(w1b - wb)
        hs = round(h1b - hb)
        w1b = round(w1b)
        h1b = round(h1b)
        dtype = image.dtype
        # cv2 的 scale 和本函数的 scale 定义相反
        rotation_matrix = cv2.getRotationMatrix2D((w1b, h1b), -degree, 1 / scale)
        img = cv2.warpAffine(img.astype(np.float32), rotation_matrix, (w1b*2+1, h1b*2+1))      # flags=cv2.INTER_NEAREST
        left = ws
        right = ws + w
        up = hs
        down = hs + h
        return img[up: down, left: right].astype(dtype)
