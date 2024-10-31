from typing import Tuple, Union, Optional
import shapely
from shapely.geometry.base import BaseGeometry

from .definition import Shape, Single, Multi, MIN_AREA


"""
这一批函数之所以单独放到 functional 里，是因为它们的逻辑调用关系与 reverse 高度相关
如果不拆成两族函数，代码写起来会非常臃肿
所以你会发现，这里只有一些集合论相关的运算
并且这里是直接对接 shapely 库的实现，并不处理基于 reverse 的逻辑关系（这些关系在上一层函数中已经处理过了）
"""


Position = Union[str, complex, Tuple[float, float]]


def inter(self: Shape, other: Shape, reverse: bool) -> Shape:
    geo = self.geo.intersection(other.geo)
    return norm_multi(geo, reverse=reverse)


def union(self: Shape, other: Shape, reverse: bool) -> Shape:
    geo = self.geo.union(other.geo)
    return norm_multi(geo, reverse=reverse)


def diff(self: Shape, other: Shape, reverse: bool) -> Shape:
    geo = self.geo.symmetric_difference(other.geo)
    return norm_multi(geo, reverse=reverse)


def remove(self: Shape, other: Shape, reverse: bool) -> Shape:
    geo = self.geo.difference(other.geo)
    return norm_multi(geo, reverse=reverse)


def norm_single(geo: BaseGeometry, reverse: bool) -> Single:
    geo = norm_geo(geo)
    if geo is None:
        return Shape.FULL if reverse else Shape.EMPTY
    if isinstance(geo, shapely.Polygon):
        return Single.COMPLEX(geo=geo)
    # 这里如果 geo 跑出来是 multi，而我需要将它按 single 去标准化，就有可能出现异常，异常控制代码在 Single.asComplex 方法里
    multi = Multi.COMPLEX(geo=geo, reverse=reverse)
    return Single.asComplex(multi)


def norm_multi(geo: BaseGeometry, reverse: bool) -> Multi:
    geo = norm_geo(geo)
    if geo is None:
        return Shape.FULL if reverse else Shape.EMPTY
    # 这里如果 geo 跑出来是 multi，而我需要把它变成 single，就需要调用 as 方法了
    if isinstance(geo, shapely.Polygon):
        geo = shapely.MultiPolygon(polygons=[geo])
    return Multi.COMPLEX(geo=geo, reverse=reverse)


def norm_geo(geo: BaseGeometry) -> Optional[BaseGeometry]:
    # 输入检查，处理各种妖魔鬼怪，这里比较重要的是最小面积阈值，需要在每次使用时定义
    if geo is None or geo.is_empty or geo.area <= MIN_AREA:
        return None
    # geo 可能存在自相交的曲线, 也可能 multigeo = [g1, g2] 并且 g1、g2 相交
    # buff(0) 好像可以消灭一切牛鬼蛇神, unary_union 则只能解决后者，遇到前者直接报错
    if not geo.is_valid or not geo.is_simple:
        geo = geo.buffer(0)

    # shapely 中只有 polygon 有面积，因此本工具库也只处理 polygon 或可能包含 polygon 的元素
    if isinstance(geo, shapely.Polygon):
        return geo

    if isinstance(geo, shapely.MultiPolygon):
        return geo

    if isinstance(geo, shapely.GeometryCollection):
        polygons = [g for g in geo.geoms if isinstance(g, shapely.Polygon)]
        geo = shapely.MultiPolygon(polygons=polygons)
        return geo

    return None
