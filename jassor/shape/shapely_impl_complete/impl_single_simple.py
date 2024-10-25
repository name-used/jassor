from typing import List, Tuple
from shapely.geometry.base import BaseGeometry
from shapely.geometry.geo import Polygon as StandardPolygon

from .definition import Shape, Single
from .impl_single_complex import ComplexPolygon
from .shapely_utils import boundary2coords


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
    ):
        if single is not None:
            assert isinstance(single, Single), 'Multi 类型无法转换为 Single'
            single = single.outer
        elif geo is not None:
            assert isinstance(geo, StandardPolygon), 'geo 必须是 Polygon'
            assert geo.boundary.type.upper() == 'LINESTRING', 'boundary 必须是 lineString'
        super().__init__(outer=outer, geo=geo, single=single)

    @property
    def outer(self) -> Single:
        # 外轮廓(正形)
        return self.copy()

    @property
    def inner(self) -> Shape:
        # 内轮廓(负形)
        return Shape.EMPTY

    def sep_in(self) -> Tuple[List[Single], List[Single]]:
        # 内分解
        return [self.copy()], []

    def sep_out(self) -> List[Single]:
        # 外分解
        return [self.copy()]

    def sep_p(self) -> List[Tuple[int, int]]:
        # 点分解
        return boundary2coords(self.geo.boundary)[0]

    @property
    def cls(self) -> type:
        return SimplePolygon


Single.SIMPLE = SimplePolygon
