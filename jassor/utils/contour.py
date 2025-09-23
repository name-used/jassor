import cv2
import numpy as np
import jassor.shape as S
from skimage.morphology import binary_opening, binary_closing, square

kernel = square(3)


def find_contour(mask: np.ndarray) -> S.MultiComplexPolygon:
    """
    从图像中提取轮廓，要求输入是一组标记图
    :param mask:    轮廓标记图，数据结构（h, w）: bool
    :return:        轮廓提取组，返回MultiComplexShape，若无元素，返回 EMPTY
    """
    mask = binary_opening(mask, footprint=kernel)
    mask = binary_closing(mask, footprint=kernel)
    contours, hierarchy = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:   # hierarchy[0] = [(next, prev, child, parent)]
        return S.EMPTY
    groups = {}
    for index, (contour, h) in enumerate(zip(contours, hierarchy[0])):
        if h[-1] == -1:
            groups[index] = [contour[:, 0, :], []]
    for index, (contour, h) in enumerate(zip(contours, hierarchy[0])):
        if h[-1] != -1:
            groups[h[-1]][1].append(contour[:, 0, :])
    shapes = [S.ComplexPolygon(outer, inners) for outer, inners in groups.values()]
    shape = S.MultiComplexPolygon(shapes=shapes)
    return shape
