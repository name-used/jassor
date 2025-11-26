from .interface import Reader
import numpy as np
import cv2
from typing import Tuple, Union, List


def crop(slide: Reader, center: Tuple[float, float], size: Union[int, Tuple[int, int]], degree: float = 0, scale: float = 1, nearest: bool = True, pad_item: Union[int, List[int]] = 0) -> np.ndarray:
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
    # slide_info = get_slide_info(slide.path)
    cx, cy = center
    w, h = (int(size), int(size)) if np.isscalar(size) else map(int, size)

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

    # 以上逻辑与 image-cropper 一致，以下部分需要新建支持函数
    return slide_remap_level0(
        slide=slide,
        map_x=map_x,
        map_y=map_y,
        nearest=nearest,
        pad_item=pad_item
    )


def slide_remap_level0(
    slide: Reader,
    map_x: np.ndarray,
    map_y: np.ndarray,
    nearest: bool = True,
    pad_item: Union[int, float, List[float]] = 0,
):
    l = int(np.floor(np.min(map_x)))
    u = int(np.floor(np.min(map_y)))
    r = int(np.ceil(np.max(map_x))) + 1
    d = int(np.ceil(np.max(map_y))) + 1

    # 从 slide level=0 读出这块 ROI
    region = slide.region(0, l, u, r, d)
    W, H = slide.dimension(0)  # 注意 TiffSlide 是 (width, height)

    # 超采样区域染色
    if l < 0:
        region[:, :0-l, ...] = pad_item
    if u < 0:
        region[:0-u, ...] = pad_item
    if d > H:
        region[H-d:, ...] = pad_item
    if r > W:
        region[:, W-r:, ...] = pad_item

    # 把 map_x/map_y 平移到 ROI 局部坐标
    map_x_local = (map_x - l).astype(np.float32)
    map_y_local = (map_y - u).astype(np.float32)

    interp = cv2.INTER_NEAREST if nearest else cv2.INTER_LINEAR

    # pad_item: 标量时 OpenCV 会自动对所有通道复制；
    # 多通道时也可以给一个 tuple/list
    if nearest:
        return cv2.remap(
            region,
            map_x_local,
            map_y_local,
            interpolation=interp,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=pad_item,
        )
    return cv2.remap(
        region.astype(np.float64),
        map_x_local,
        map_y_local,
        interpolation=interp,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=pad_item,
    ).astype(region.dtype)
