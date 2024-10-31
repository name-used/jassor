from typing import List, Tuple

import shapely
from shapely.geometry.base import BaseGeometry

from .definition import Shape, Single, CoordinatesNotLegalException, NoParametersException
from .impl_single_complex import ComplexPolygon
import functional as F


class SimplePolygon(ComplexPolygon):
    """
    单-单连通多边形, 创建方式有三:
    1. 指定 outer
    2. 指定 geo
    3. 指定 single
    遵循逆序优先规则
    当 polygon 是 ComplexPolygon 时, 忽视其内轮廓
    """

    __slots__ = ()

    def __init__(
            self,
            outer: List[Tuple[float, float]] = None,
            geo: BaseGeometry = None,
            single: Single = None,
            from_p: List[Tuple[float, float]] = None,
            reverse: bool = False
    ):
        if geo is not None:
            assert isinstance(geo, shapely.MultiPolygon), 'geo 必须是 MultiPolygon'
            assert all(g.boundary.type.upper() == 'LINESTRING' for g in geo.geoms), 'geo 必须是单连通的'
        elif single is not None:
            assert isinstance(single, Single), 'Multi 类型无法转换为 Single'
            geo = single.geo
        elif from_p is not None:
            outer = from_p
            geo = shapely.Polygon(shell=outer, holes=[])
        elif outer is not None:
            # 对用户输入进行检查和修复
            geo = shapely.Polygon(shell=outer, holes=[])
            geo = F.norm_geo(geo)
            # 创建时要求轮廓必须合法
            if geo is None or isinstance(geo, shapely.MultiPolygon):
                raise CoordinatesNotLegalException(f'creating single polygon with geo=={type(geo)}')
            # 还得是单连通的
            if bool(geo.interiors):
                raise CoordinatesNotLegalException(f'SimplePolygon not allowed interiors coordinates with geo interiors nums: {len(geo.interiors)}')
        else:
            # 没有任何参数的话，要报个错
            raise NoParametersException(f'Any of such parameters have to be provided: outer, geo, single, from_p')
        super().__init__(None, geo=geo, single=None, from_p=None, reverse=reverse)

    @property
    def outer(self) -> Single:
        # 外轮廓(正形)
        return Single.SIMPLE(geo=self.geo)

    @property
    def inner(self) -> Shape:
        # 内轮廓(负形)
        return Shape.EMPTY

    def sep_out(self) -> List[Single]:
        # 外分解
        return [Single.SIMPLE(geo=self.geo)]

    def sep_p(self) -> List[Tuple[float, float]]:
        # 点分解
        outer = list(shapely.get_exterior_ring(self.geo).coords)
        return outer

    @property
    def cls(self) -> type:
        return SimplePolygon


Single.SIMPLE = SimplePolygon
