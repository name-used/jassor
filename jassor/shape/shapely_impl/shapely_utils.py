from typing import List, Tuple


# 将 shapely 千奇百怪的轮廓统一分解为 外轮廓 + 内轮廓数组 的固定格式
def boundary2coords(boundary) -> Tuple[
    List[Tuple[int, int]],
    List[List[Tuple[int, int]]]
]:
    if boundary.type.upper() == 'LINESTRING':
        return list(boundary.coords), []
    elif boundary.type.upper() == 'MULTILINESTRING':
        outer, *inner = boundary
        return list(outer.coords), [list(i.coords) for i in inner]
    else:
        raise Exception(f'起床了, 快来处理bug -> {boundary.type} -> {boundary}')


'''
关于 shapely 中的类型:
'Point',
'LineString',
'LinearRing',
'Polygon',
'MultiPoint',
'MultiLineString',
'MultiPolygon',
'GeometryCollection',
事实上, LinearRing 是一个只存在于文档中的类型, 至少在代码的输出看来,
即便向多边形中认真的手动传入一个 linearRing, 它的输出值依然是 LineString
'''
