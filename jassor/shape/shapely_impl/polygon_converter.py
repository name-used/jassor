from typing import Literal, Tuple, List

import cv2
import numpy as np
from skimage.morphology import binary_opening, binary_closing, square

from .definition import Shape, Multi
from .impl_single_simple import SimplePolygon
from .impl_single_complex import ComplexPolygon
from .impl_multi_complex import MultiComplexPolygon
from .polygon_creators import create_from_hierarchy


def convert_mask2shape(mask: np.ndarray, ksize: int = 0) -> MultiComplexPolygon:
    """
    从图像中提取轮廓，要求输入是一组标记图
    :param mask:    轮廓标记图，数据结构（h, w）: bool
    :param ksize:   开闭运算的核尺寸
    :return:        轮廓提取组，返回MultiComplexShape，若无元素，返回 EMPTY
    """
    if ksize > 0:
        kernel = square(ksize)
        mask = binary_closing(mask, footprint=kernel)
        mask = binary_opening(mask, footprint=kernel)
    contours, hierarchy = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:  # hierarchy[0] = [(next, prev, child, parent)]
        return Shape.EMPTY
    return create_from_hierarchy(contours, hierarchy)


def convert_shape2mask(shape: Shape, bsize: int = 10, bbox_mode: Literal['float', 'absolute'] = 'float') -> np.ndarray:
    if shape == Shape.EMPTY:
        return np.zeros((bsize*2, bsize*2), dtype=np.uint8)
    if shape == Shape.FULL:
        return np.ones((bsize*2, bsize*2), dtype=np.uint8)
    l, u, r, d = map(round, shape.bounds)
    l -= bsize
    u -= bsize
    r += bsize
    d += bsize
    if bbox_mode == 'absolute':
        l = u = 0
    shape = shape - (l, u)
    mask = np.zeros((d-u, r-l), dtype=np.uint8)
    # 统一用最大的图形处理，避免多重语义困扰（这也是我设计这套封装库的初衷）
    shape = Multi.asComplex(shape)
    for poly in shape:
        outer, inners = poly.sep_p()
        contours = [np.asarray(coords).round().astype(np.int64) for coords in [outer, *inners]]
        cv2.fillPoly(mask, [contours], 1)
    if shape.reversed:
        mask = 1 - mask
    return mask


def convert_geojson2shapes(geojson) -> Tuple[List[Shape], List[dict]]:
    if 'features' in geojson:
        geojson = geojson['features']
    shapes = []
    props = []
    for item in geojson:
        tp = item['geometry']['type']
        coords = item['geometry']['coordinates']
        # shape 没封装点，emm……遇到点就不处理了，直接原值抛回
        if tp.lower() == 'point' or tp.lower() == 'multipoint':
            shape = coords
        elif tp.lower() == 'linestring' or tp.lower() == 'linering':
            shape = SimplePolygon(outer=coords)
        elif tp.lower() == 'polygon':
            shape = ComplexPolygon(outer=coords[0], inners=coords[1:])
        elif tp.lower() == 'multipolygon':
            outers = []
            inners = []
            adjs = []
            for cds in coords:
                inners.extend(cds[1:])
                adjs.extend([len(outers)] * len(cds[1:]))
                outers.append(cds[0])
            shape = MultiComplexPolygon(outers=outers, inners=inners, adjacencies=adjs)
        else:
            raise f'Unknown type {tp}'
        shapes.append(shape)
        props.append({'shape_type': tp.lower(), **item['properties']})
    return shapes, props


def convert_shapes2geojson(shapes: List[Shape], props: List[dict] = None):
    """
    你的 geojson2shapes() 的逆：
    输入 shapes: List[dict]，每个 dict 至少包含 {'shape': ..., 'shape_type': ...}，其余字段会进 properties
    输出 FeatureCollection
    """
    features = []
    props = props or [{}] * len(shapes)
    for shape, prop in zip(shapes, props):
        geom = _shape2geometry(shape)
        prop.pop("shape", None)
        prop.pop("shape_type", None)
        features.append({
            "type": "Feature",
            "properties": props,
            "geometry": geom,
        })
    return {"type": "FeatureCollection", "features": features}


def _shape2geometry(shape: Shape):
    """
    shape -> GeoJSON geometry(dict)
    支持：SimplePolygon / ComplexPolygon / MultiComplexPolygon
    以及：点坐标(list/tuple)原样映射为 Point
    """
    if shape is None:
        return {"type": "Polygon", "coordinates": []}

    # Point: [x, y] / (x, y)
    if isinstance(shape, (list, tuple)) and len(shape) == 2 and all(isinstance(v, (int, float)) for v in shape):
        return {"type": "Point", "coordinates": list(shape)}

    # MultiComplexPolygon: outers, inners, adjacencies
    if hasattr(shape, "outers") and hasattr(shape, "inners") and hasattr(shape, "adjacencies"):
        outers = [_close_ring(o) for o in getattr(shape, "outers")]
        inners = [_close_ring(i) for i in getattr(shape, "inners")]
        adjs = list(getattr(shape, "adjacencies"))

        grouped = [[] for _ in range(len(outers))]
        for inner, oi in zip(inners, adjs):
            if 0 <= oi < len(grouped):
                grouped[oi].append(inner)

        coords = [[outers[i]] + grouped[i] for i in range(len(outers))]
        # 约定：无外壳就是 empty
        if len(coords) == 0:
            return {"type": "Polygon", "coordinates": []}
        return {"type": "MultiPolygon", "coordinates": coords}

    # ComplexPolygon: outer, inners
    if hasattr(shape, "outer") and hasattr(shape, "inners"):
        outer = _close_ring(getattr(shape, "outer"))
        inners = [_close_ring(i) for i in getattr(shape, "inners")]
        if not outer:
            return {"type": "Polygon", "coordinates": []}
        return {"type": "Polygon", "coordinates": [outer] + inners}

    # SimplePolygon: outer
    if hasattr(shape, "outer"):
        outer = _close_ring(getattr(shape, "outer"))
        if not outer:
            return {"type": "Polygon", "coordinates": []}
        return {"type": "Polygon", "coordinates": [outer]}

    raise TypeError(f"Unsupported shape type: {type(shape)!r}")


def _close_ring(ring):
    if not ring:
        return ring
    a, b = ring[0], ring[-1]
    return ring if (a[0] == b[0] and a[1] == b[1]) else (list(ring) + [a])
