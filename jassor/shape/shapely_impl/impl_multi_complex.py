from typing import List, Tuple, Iterable
from shapely.geometry.base import BaseGeometry
from shapely.geometry.geo import MultiPolygon as StandardMultiPolygon
from shapely.geometry.geo import Polygon as StandardPolygon

from .definition import Shape, Single, Multi
from .impl_base import Base


class ComplexMultiPolygon(Base, Multi):
    """
    多-复连通多边形, 创建方式有五:
    1. 指定 outers
    2. 指定 outers, inners, adjacencies
    3. 指定 geo
    4. 指定 Single 数组
    5. 指定 Multi
    遵循逆序优先规则
    """

    def __init__(
            self,
            outers: List[Tuple[float, float]] = None,
            inners: List[Tuple[float, float]] = None,
            adjacencies: List[int] = None,

            geo: BaseGeometry = None,

            singles: Iterable[Single] = None,

            multi: Multi = None,
    ):
        if multi is not None:
            assert isinstance(multi, Multi), '将 Simple 转化为 Multi 请通过 singles 指定'
            geo = multi.geo
        elif singles is not None:
            coords = [Single.asComplex(single).sep_p() for single in singles if single.is_valid()]
            if len(coords) == 1:
                geo = StandardPolygon(shell=coords[0][0], holes=coords[0][1])
            else:
                geo = StandardMultiPolygon(polygons=coords)
        elif geo is not None:
            assert isinstance(geo, StandardMultiPolygon), 'geo 必须是 MultiPolygon'
        else:
            assert outers is not None, 'Parameters could not be all empty!'
            if inners is None and adjacencies is None:
                coords = [(outer, []) for outer in outers]
            else:
                assert inners is not None and adjacencies is not None and len(inners) == len(adjacencies), '孔洞未对齐'
                coords = [
                    (outer, [inner for j, inner in enumerate(inners) if adjacencies[j] == i])
                    for i, outer in enumerate(outers)
                ]
            geo = StandardMultiPolygon(polygons=coords)
        super().__init__(geo=geo)

    def merge(self, other: Shape) -> Multi:
        # 合集运算
        if not other: return Multi.asComplex(self)
        geo = self.geo
        singles = other.sep_out()
        geos = [s.geo for s in singles if not geo.disjoint(s.geo)]
        for g in geos:
            geo = geo.union(g)
        multi = self.__norm_multi__(geo)
        return ComplexMultiPolygon(multi=multi)

    @property
    def outer(self) -> Multi:
        # 外轮廓(正形)
        return Multi.SIMPLE(singles=self.sep_in()[0])

    @property
    def inner(self) -> Multi:
        # 内轮廓(负形)
        inners = self.sep_in()[1]
        if not inners: return Multi.EMPTY
        return Multi.SIMPLE(singles=inners)

    def sep_in(self) -> Tuple[List[Single], List[Single]]:
        # 内分解
        # 逐层分解 (规避由 shapely 任意性引起的荒诞错误)
        singles = [Single.COMPLEX(geo=g) for g in self.geo.geoms if isinstance(g, StandardPolygon)]
        singles = [s for s in singles if s.is_valid()]
        outers = []
        inners = []
        for s in singles:
            o, i = s.sep_in()
            outers.extend(o)
            inners.extend(i)
        return outers, inners

    def sep_out(self) -> List[Single]:
        # 外分解
        singles = [Single.COMPLEX(geo=g) for g in self.geo.geoms if isinstance(g, StandardPolygon)]
        singles = [s for s in singles if s.is_valid()]
        return singles

    def sep_p(self) -> Tuple[
        List[List[Tuple[int, int]]],
        List[List[Tuple[int, int]]],
        List[int]
    ]:
        # 点分解
        # 逐层分解 (规避由 shapely 任意性引起的荒诞错误)
        singles = [Single.COMPLEX(geo=g) for g in self.geo.geoms if isinstance(g, StandardPolygon)]
        singles = [s for s in singles if s.is_valid()]
        outers = []
        inners = []
        adjacencies = []
        for i, single in enumerate(singles):
            p, qs = single.sep_p()
            outers.append(p)
            inners.extend(qs)
            adjacencies.extend([i] * len(qs))
        return outers, inners, adjacencies

    @property
    def cls(self) -> type:
        return ComplexMultiPolygon


Multi.COMPLEX = ComplexMultiPolygon
