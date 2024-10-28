from typing import List, Tuple

import shapely
from shapely.geometry.base import BaseGeometry

from .definition import Shape, Single
from .impl_single_complex import ComplexPolygon


class SimplePolygon(ComplexPolygon):
    """
    单-单连通多边形, 创建方式有三:
    1. 指定 outer
    2. 指定 geo
    3. 指定 single
    遵循逆序优先规则
    当 polygon 是 ComplexPolygon 时, 忽视其内轮廓
    """

    def __init__(
            self,
            outer: List[Tuple[float, float]] = None,
            geo: BaseGeometry = None,
            single: Single = None,
            from_p: List[Tuple[float, float]] = None,
            reverse: bool = False
    ):
        if from_p is not None:
            outer = from_p
        super().__init__(outer, geo=geo, single=single, from_p=None, reverse=reverse)

    @property
    def outer(self) -> Single:
        # 外轮廓(正形)
        return Single.asSimple(self)

    @property
    def inner(self) -> Shape:
        # 内轮廓(负形)
        return Shape.EMPTY

    def sep_in(self) -> Tuple[Single, Shape.EMPTY]:
        # 内分解
        return self.outer, self.inner

    def sep_out(self) -> List[Single]:
        # 外分解
        return [Single.asSimple(self)]

    def sep_p(self) -> List[Tuple[int, int]]:
        # 点分解
        outer = list(shapely.get_exterior_ring(self.geo).coords)
        return outer

    @property
    def cls(self) -> type:
        return SimplePolygon


Single.SIMPLE = SimplePolygon
