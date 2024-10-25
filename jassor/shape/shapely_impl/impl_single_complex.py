from typing import List, Tuple
from shapely.geometry.base import BaseGeometry
from shapely.geometry.geo import Polygon as StandardPolygon

from .definition import Shape, Single, Multi
from .impl_base import Base
from .shapely_utils import boundary2coords


class ComplexPolygon(Base, Single):
    """
    单-复连通多边形, 创建方式有三:
    1. 指定 outer, *inners
    2. 指定 geo
    3. 指定 single
    遵循逆序优先规则
    """

    def __init__(
            self,
            outer: List[Tuple[float, float]] = None,
            *inners: List[Tuple[float, float]],
            geo: BaseGeometry = None,
            single: Single = None,
    ):
        if single is not None:
            assert isinstance(single, Single), 'Multi 类型无法转换为 Single'
            geo = single.geo
        elif geo is not None:
            assert isinstance(geo, StandardPolygon), 'geo 必须是 Polygon'
        elif outer is not None:
            geo = StandardPolygon(shell=outer, holes=inners)
        else:
            raise ValueError('Parameters could not be all empty!')
        super().__init__(geo=geo)

    def merge(self, other: Shape) -> Single:
        # 合集运算
        if not other: return Multi.asComplex(self)
        geo = self.geo
        singles = other.sep_out()
        geos = [s.geo for s in singles if not geo.disjoint(s.geo)]
        for g in geos:
            geo = geo.union(g)
        single = self.__norm_single__(geo)
        return ComplexPolygon(single=single)

    @property
    def outer(self) -> Single:
        # 外轮廓(正形)
        return Single.SIMPLE(single=self.sep_in()[0][0])

    @property
    def inner(self) -> Multi:
        # 内轮廓(负形)
        inners = self.sep_in()[1]
        if not inners: return Multi.EMPTY
        return Multi.SIMPLE(singles=inners)

    def sep_in(self) -> Tuple[List[Single], List[Single]]:
        # 内分解
        outer, inners = boundary2coords(self.geo.boundary)
        outers = [Single.SIMPLE(outer=outer)]
        inners = [Single.SIMPLE(outer=inner) for inner in inners]
        return outers, inners

    def sep_out(self) -> List[Single]:
        # 外分解
        return [self]

    def sep_p(self) -> Tuple[
        List[Tuple[int, int]],
        List[List[Tuple[int, int]]]
    ]:
        # 点分解
        return boundary2coords(self.geo.boundary)

    @property
    def cls(self) -> type:
        return ComplexPolygon


Single.COMPLEX = ComplexPolygon
