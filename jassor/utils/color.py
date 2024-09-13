from typing import List, Tuple
import random
import cv2
import numpy as np


def random_colors(
        n: int,
        start: Tuple[int, int, int] = (47, 81, 177),
        step: Tuple[int, int, int] = (73, 119, 31),
        rand: Tuple[int, int, int] = (10, 10, 10),
) -> List[Tuple[int, int, int]]:
    """
    生成一组随机色值，在一定程度上保证相邻色值间存在显著的用色差异，不关心色值是否存在复用现象
    :param n:       生成颜色数量
    :param start:   第一个颜色
    :param step:    颜色渐变公式（线性）
    :param rand:    随机因子
    :return:
    """
    r, g, b = start
    result = [(r, g, b)]
    while len(result) < n:
        r, g, b = [
            (
                c + step[i] + random.randint(-rand[i], +rand[i])
            ) % 255 for i, c in enumerate([r, g, b])
        ]
        result.append((r, g, b))
    return result


def random_rainbow_curves(
    shape: Tuple[int, int, int],
    s: int = 117,
    k: int = 7,
    c: int = 50,
):
    """
    生成一组随机色斑
    :param shape:   所生成的图像尺寸 (h, w, c)，按需取值
    :param s:       取值越大，色斑的尺寸越大，（影响速度），取值必须是奇数，推荐取值为图像尺寸的十分之一
    :param k:       迭代次数，取值越大，图案越平滑，（影响速度），推荐取值 0 - 20
    :param c:       对比度系数，取值越大，图案对比越强烈，推荐取值 0 - 100
    :return:
    """
    # 先生成噪声图
    h, w, nc = shape
    bg = np.random.random(w * h * nc).reshape((h, w, nc))
    bg = (np.clip(bg, 0, 1) * 256).astype(np.uint8)
    # 再将噪声图处理成背景干扰图像
    for _ in range(k):
        # 颜色空间拉伸，显眼化
        bg = bg.clip(c, 255 - c) - c
        bg = (bg / (255 - 2 * c) * 255).astype(np.uint8)
        # 用中值滤波对均值滤波做差，实现色斑合并
        m1 = cv2.blur(bg, (s, s))
        m2 = cv2.medianBlur(bg, s)
        bg = np.clip(2 * m2.astype(int) - m1.astype(int), 0, 255).astype(np.uint8)
    return bg
