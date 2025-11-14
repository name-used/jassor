from typing import Tuple, List, Union
import numpy as np
import cv2


def crop(image: np.ndarray, center: Tuple[float, float], size: Union[int, Tuple[int, int]], degree: float = 0, scale: float = 1, nearest: bool = True, pad_item: Union[int, List[int]] = 0) -> np.ndarray:
    """
        切图函数，用于切割给定图像，参数含义如下所示：
        1. 定义一个尺寸为 size 的窗口
        2. 将窗口依 scale 倍数缩放（scale > 1 时窗口变大）
        3. 将窗口旋转 degree 角度（按矩阵逆时针、图像顺时针顺序）
        4. 将窗口中心平移至图像的 center 处
        5. 用窗口在 image 中切取数据，当 nearest 为真时，切取数据均来自 image 原图最近相关点，否则来自邻近点的线性运算
        6. 所采集点回归收拢至原窗口，形成一张尺寸为 size 的图像
        请注意：图像与矩阵的顺逆时针顺序相反，图像逆时针对应矩阵顺时针
        当 degree>0、scale>1 时，图像看起来是逆时针旋转、视野变大、元素尺寸变小
    """
    cx, cy = center
    w, h = (int(size), int(size)) if np.isscalar(size) else map(int, size)
    if len(image.shape) == 2:
        pad_item = pad_item if np.isscalar(pad_item) else pad_item[0]
        return _crop(image, cx, cy, w, h, degree, scale, nearest, pad_item)
    elif len(image.shape) == 3:
        pad_item = [pad_item] * image.shape[2] if np.isscalar(pad_item) else pad_item
        results = [_crop(image[:, :, i], cx, cy, w, h, degree, scale, nearest, pad_item[i]) for i in range(image.shape[2])]
        return np.stack(results, axis=2)
    else:
        raise ValueError(f'Shape of image must be array[y, x] or array[y, x, c], but found {type(image)} - {image.shape}')


def _crop(image, cx, cy, w, h, degree, scale, nearest, pad_item) -> np.ndarray:
    # 输出 patch 网格（x/y 相对中心）
    x_grid, y_grid = np.meshgrid(np.arange(w), np.arange(h))          # shape (h, w)
    x_grid = x_grid - (w - 1) / 2.0
    y_grid = y_grid - (h - 1) / 2.0

    # 角度／scale 变换：你想要的「取景框旋转 + 缩放」
    theta = np.deg2rad(degree)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    # 先 scale，再旋转（这里是图像看起来顺时针为正角）
    dx_src = scale * (cos_t * x_grid - sin_t * y_grid)
    dy_src = scale * (sin_t * x_grid + cos_t * y_grid)

    x_src = cx + dx_src
    y_src = cy + dy_src

    # remap 需要 float32 的 map
    map_x = x_src.astype(np.float32)
    map_y = y_src.astype(np.float32)

    # 选择插值方式
    interp = cv2.INTER_NEAREST if nearest else cv2.INTER_LINEAR

    # borderValue 用 pad_item，保持 dtype 一致即可
    # 注意：OpenCV 期望 H×W×C 的顺序，多通道自动处理
    if nearest:
        return cv2.remap(
            image,
            map_x,
            map_y,
            interpolation=interp,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=pad_item,
        )
    return cv2.remap(
        image.astype(np.float64),
        map_x,
        map_y,
        interpolation=interp,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=pad_item,
    ).astype(image.dtype)
