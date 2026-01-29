from typing import List, Tuple

from shapely.geometry import LinearRing, MultiLineString, Polygon
from shapely.ops import unary_union, polygonize

XY = Tuple[float, float]
Ring = List[XY]


def deintersect(coords: Ring) -> List[Ring]:
    """
    输入：闭合或不闭合的 ring coords
    输出：若 ring 本身 simple，则 [原ring(闭合后)]
         否则：返回若干个 simple ring（每个闭合）
    只处理“自相交/自触/桥接”的拓扑合法性，不做面积/退化过滤。
    """
    if not coords:
        return []

    pts = list(coords)

    # 1) 保证闭合 & 去掉连续重复点（避免零长度边）
    if pts[0] != pts[-1]:
        pts.append(pts[0])
    cleaned = [pts[0]]
    for p in pts[1:]:
        if p != cleaned[-1]:
            cleaned.append(p)
    pts = cleaned
    if len(pts) < 4:  # 少于 3 个不同点无法成环
        return []

    # 2) 快路径：本身就是 simple ring，直接返回
    if LinearRing(pts).is_simple:
        return [pts]

    # 3) 慢路径：拆段 -> 节点化 -> polygonize -> 取每个面的 exterior 作为 ring
    segs = [[pts[i], pts[i + 1]] for i in range(len(pts) - 1) if pts[i] != pts[i + 1]]
    noded = unary_union(MultiLineString(segs))
    faces = list(polygonize(noded))

    out: List[Ring] = []
    for f in faces:
        # polygonize 出来的是 Polygon（合法面），其 exterior 就是一个 simple ring
        ring = list(f.exterior.coords)
        out.append([(float(x), float(y)) for x, y in ring])

    return out
