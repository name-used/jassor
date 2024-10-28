from typing import List, Tuple

import shapely
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import InteriorRingSequence

from .definition import Shape, Single, Multi
from .impl_base import Base


class ComplexPolygon(Base, Single):
    """
    单-复连通多边形, 创建方式有三:
    1. 指定 geo
    2. 指定 single
    3. 指定 outer, *inners
    按上述优先顺序
    """

    __slots__ = ()

    def __init__(
            self,
            outer: List[Tuple[float, float]] = None,
            *inners: List[Tuple[float, float]],
            geo: BaseGeometry = None,
            single: Single = None,
            from_p: Tuple[
                List[Tuple[float, float]],          # outer
                List[List[Tuple[float, float]]],    # inners
            ] = None,
            reverse: bool = False
    ):
        if geo is not None:
            assert isinstance(geo, shapely.Polygon), 'geo 必须是 Polygon'
        elif single is not None:
            assert isinstance(single, Single), 'Multi 类型无法转换为 Single'
            geo = single.geo
        elif from_p is not None:
            outer, inners = from_p
            geo = shapely.Polygon(shell=outer, holes=inners)
        elif outer is not None:
            geo = shapely.Polygon(shell=outer, holes=inners)
        else:
            raise ValueError('Parameters could not be all empty!')
        super().__init__(geo=geo, reverse=reverse)

    def merge(self, other: Shape) -> Single:
        # 合集运算
        if not other: return Single.asComplex(self)
        geo = self.geo
        singles = other.sep_out()
        geos = [s.geo for s in singles if not geo.disjoint(s.geo)]
        for g in geos:
            geo = geo.union(g)
        single = self.__norm_single__(geo)
        return Single.asComplex(shape=single)

    @property
    def outer(self) -> Single:
        # 外轮廓(正形)
        geo = shapely.Polygon(shell=shapely.get_exterior_ring(self.geo))
        return Single.SIMPLE(geo=geo)

    @property
    def inners(self) -> Multi:
        # 内轮廓(负形)
        inners = InteriorRingSequence(self.geo)
        inners = [shapely.Polygon(shell=inner) for inner in inners]
        geo = shapely.MultiPolygon(polygons=inners)
        if geo.is_empty:
            return Shape.EMPTY
        return Multi.SIMPLE(geo=geo)

    def sep_in(self) -> Tuple[Single, Multi]:
        # 内分解
        return self.outer, self.inners

    def sep_out(self) -> List[Single]:
        # 外分解
        return [self]

    def sep_p(self) -> Tuple[
        List[Tuple[int, int]],
        List[List[Tuple[int, int]]]
    ]:
        # 点分解
        outer = list(shapely.get_exterior_ring(self.geo).coords)
        inners = InteriorRingSequence(self.geo)
        inners = [list(inner.coords) for inner in inners]
        return outer, inners

    def comp(self):
        self._reversed = not self._reversed

    @property
    def cls(self) -> type:
        return ComplexPolygon


Single.COMPLEX = ComplexPolygon
