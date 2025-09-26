import cv2
import numpy as np
import jassor.shape as S
from skimage.morphology import binary_opening, binary_closing, square


def find_contour(mask: np.ndarray, ksize: int = 3) -> S.MultiComplexPolygon:
    """
    从图像中提取轮廓，要求输入是一组标记图
    :param mask:    轮廓标记图，数据结构（h, w）: bool
    :param ksize:   开闭运算的核尺寸
    :return:        轮廓提取组，返回MultiComplexShape，若无元素，返回 EMPTY
    """
    kernel = square(ksize)
    mask = binary_opening(mask, footprint=kernel)
    mask = binary_closing(mask, footprint=kernel)
    contours, hierarchy = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:   # hierarchy[0] = [(next, prev, child, parent)]
        return S.EMPTY
    # 将 cv2 格式改成我的格式
    outers = []
    inners = []
    adjacencies = []
    mapper = {}
    for i, (contour, h) in enumerate(zip(contours, hierarchy[0])):
        if h[-1] == -1:
            mapper[i] = len(outers)
            outers.append(contour[:, 0, :].tolist())
    for i, (contour, h) in enumerate(zip(contours, hierarchy[0])):
        if h[-1] != -1:
            inners.append(contour[:, 0, :].tolist())
            adjacencies.append(mapper[h[-1]])
    shape = S.MultiComplexPolygon(outers, inners, adjacencies)
    return shape


def geojson2shapes(geojson):
    if 'features' in geojson:
        geojson = geojson['features']
    shapes = []
    for item in geojson:
        tp = item['geometry']['type']
        coords = item['geometry']['coordinates']
        # shape 没封装点，emm……遇到点就不处理了，直接原值抛回
        if tp.lower() == 'point' or tp.lower() == 'multipoint':
            shape = coords
        elif tp.lower() == 'linestring' or tp.lower() == 'linering':
            shape = S.SimplePolygon(outer=coords)
        elif tp.lower() == 'polygon':
            shape = S.ComplexPolygon(outer=coords[0], inners=coords[1:])
        elif tp.lower() == 'multipolygon':
            outers = []
            inners = []
            adjs = []
            for cds in coords:
                inners.extend(cds[1:])
                adjs.extend([len(outers)] * len(cds[1:]))
                outers.append(cds[0])
            shape = S.MultiComplexPolygon(outers=outers, inners=inners, adjacencies=adjs)
        else:
            raise f'Unknown type {tp}'
        shapes.append({
            **item['properties'],
            'shape_type': tp.lower(),
            'shape': shape,
        })
    return shapes
