from typing import List, Tuple, Iterable
from shapely.geometry.base import BaseGeometry
from shapely.geometry.geo import MultiPolygon as StandardMultiPolygon
from shapely.geometry.geo import Polygon as StandardPolygon

from .definition import Shape, Single, Multi
from .impl_multi_complex import ComplexMultiPolygon


class SimpleMultiPolygon(ComplexMultiPolygon):
    """
    多-单连通多边形, 创建方式有四:
    1. 指定 outers
    2. 指定 geo
    3. 指定 Single 数组
    4. 指定 Multi
    遵循逆序优先规则
    """

    def __init__(
            self,
            outers: List[Tuple[float, float]] = None,
            geo: BaseGeometry = None,
            singles: Iterable[Single] = None,
            multi: Multi = None,
    ):
        if multi is not None:
            assert isinstance(multi, Multi), '将 Simple 转化为 Multi 请通过 singles 指定'
            multi = multi.outer
        elif singles is not None:
            coords = [(single.outer.sep_p(), []) for single in singles if single.is_valid()]
            geo = StandardMultiPolygon(polygons=coords)
        elif geo is not None:
            assert isinstance(geo, StandardMultiPolygon), 'geo 必须是 MultiPolygon'
            assert sum([not isinstance(g, StandardPolygon) for g in geo.geoms]) == 0, 'geo 必须由多边形组成'
            assert sum([g.boundary.type.upper() != 'LINESTRING' for g in geo.geoms]) == 0, 'geo 必须是单连通的'
        super().__init__(outers=outers, geo=geo, singles=None, multi=multi)

    # def merge(self, shape: Shape) -> Multi:
    #     # 合集运算
    #     geo = self.geo
    #     singles = shape.sep_out()
    #     geos = [s.geo for s in singles if not geo.disjoint(s.geo)]
    #     for g in geos:
    #         geo = geo.union(g)
    #     geo = self.__norm_multi__(geo)
    #     return ComplexMultiPolygon(geo=geo)

    @property
    def outer(self) -> Multi:
        # 外轮廓(正形)
        return self.copy()

    @property
    def inner(self) -> Multi:
        # 内轮廓(负形)
        return Shape.EMPTY

    def sep_in(self) -> Tuple[List[Single], List[Single]]:
        # 内分解
        # 逐层分解 (规避由 shapely 的任意性引起的荒诞错误)
        singles = [Single.SIMPLE(geo=g) for g in self.geo.geoms if isinstance(g, StandardPolygon)]
        singles = [s for s in singles if s.is_valid()]
        return singles, []

    def sep_out(self) -> List[Single]:
        # 外分解
        singles = [Single.SIMPLE(geo=g) for g in self.geo.geoms if isinstance(g, StandardPolygon)]
        singles = [s for s in singles if s.is_valid()]
        return singles

    def sep_p(self) -> List[List[Tuple[int, int]]]:
        # 点分解
        # 逐层分解 (规避由 shapely 任意性引起的荒诞错误)
        singles = [Single.SIMPLE(geo=g) for g in self.geo.geoms if isinstance(g, StandardPolygon)]
        singles = [s for s in singles if s.is_valid()]
        return [s.sep_p() for s in singles if s.is_valid()]

    @property
    def cls(self) -> type:
        return SimpleMultiPolygon


Multi.SIMPLE = SimpleMultiPolygon
