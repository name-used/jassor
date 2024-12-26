from typing import Tuple
import math
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
    H, W = image.shape
    x_center, y_center = center
    w, h = map(int, (size, size) if isinstance(size, (int, float)) else size)
    wb = (w - 1) / 2
    hb = (h - 1) / 2
    r = degree * np.pi / 180
    sina, cosa = np.sin(r), np.cos(r)
    w1b = round((wb * abs(cosa) + hb * abs(sina)) * scale)
    h1b = round((hb * abs(cosa) + wb * abs(sina)) * scale)
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


# x = np.arange(100).reshape(10, 10)
# print(x)
# print(crop(x, (5, 5), (5, 5), degree=15, scale=2))
# print(crop(x, (5, 5), (5, 5), degree=15, scale=2, nearest=False))

# x = cv2.imread(rf'../../resources/test.jpg', flags=cv2.IMREAD_GRAYSCALE)
# from jassor.utils.jassor_plot_lib import plot
# plot(x)
# plot(crop(x, (960, 540), (400, 400), degree=15, scale=2))
# plot(crop(x, (960, 540), (400, 400), degree=15, scale=2, nearest=False))

#
# @abc.abstractmethod
# def slide(self, x, y, width, height):
#     raise NotImplemented('please implement it in sub-class of RotateCropper')
#
#
# def rotate(array: np.ndarray, degree: float, scale: float = 1, padding: np.ndarray = np.array(0)):
#     """
#     :param array: Numpy(height, width, ...) to be rotated
#     :param degree: anti-clock -> float[-180, +180]
#     :param scale: float > 0
#     :param padding: a default vector to init result
#     :return: Numpy(HEIGHT, WIDTH, ...) -> a bigger numpy
#     """
#     assert array is not None and len(array.shape) >= 2, 'array should be an image-matrix, got {}'.format(array.shape if array else None)
#     # init a temp
#     r = degree * np.pi / 180
#     sina, cosa = np.sin(r), np.cos(r)
#     h, w = array.shape[:2]
#     w1 = math.ceil((w * abs(cosa) + h * abs(sina)) / scale)
#     h1 = math.ceil((h * abs(cosa) + w * abs(sina)) / scale)
#     # temp = np.zeros(shape=(h1, w1) + array.shape, dtype=array.dtype)
#     # temp[:, :] = padding
#
#     # warp_affine -> https://blog.csdn.net/qq_40939814/article/details/117966835
#     # build map-matrix
#     x_grid, y_grid = np.meshgrid(np.arange(w1), np.arange(h1))
#     x_grid = x_grid - w1 / 2
#     y_grid = y_grid - h1 / 2
#     x_index = ((cosa * x_grid + sina * y_grid)*scale + w / 2).round().astype(np.int32)
#     y_index = ((cosa * y_grid - sina * x_grid)*scale + h / 2).round().astype(np.int32)
#     # mapping
#     condition = (x_index >= 0) & (x_index < w) & (y_index >= 0) & (y_index < h)
#     # x_index[np.logical_not(condition)] = 0
#     # y_index[np.logical_not(condition)] = 0
#     # print(w, h, w1, h1, array.shape, condition.shape, x_index[condition].max(), y_index[condition].max())
#     # print(array.shape, condition.shape, padding.shape)
#     # expand dims and use the numpy-broadcast
#     condition = np.expand_dims(condition, tuple(range(2, len(array.shape))))
#     padding = np.expand_dims(padding, tuple(range(len(array.shape) - 2)))
#     return np.where(
#         condition,
#         array[
#             np.clip(y_index, 0, h-1),
#             np.clip(x_index, 0, w-1),
#         ],
#         padding
#     )
#
#
# def get_size_rate(degree: float):
#     radius = degree * np.pi / 180
#     sina = np.sin(radius)
#     cosa = np.cos(radius)
#     return abs(sina) + abs(cosa)
