from typing import List, Tuple

import shapely
from shapely.geometry.base import BaseGeometry

from .definition import Shape, Single, Multi, CoordinatesNotLegalException, NoParametersException
from .impl_base import Base
import functional as F


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
            # 对用户输入进行检查和修复
            geo = shapely.Polygon(shell=outer, holes=inners)
            geo = F.norm_geo(geo)
            # 创建时要求轮廓必须合法
            if geo is None or isinstance(geo, shapely.MultiPolygon):
                raise CoordinatesNotLegalException(f'creating single polygon with geo=={type(geo)}')
        else:
            # 没有任何参数的话，要报个错
            raise NoParametersException(f'Any of such parameters have to be provided: (outer, *inners), geo, single, from_p')
        super().__init__(geo=geo, reverse=reverse)

    @property
    def outer(self) -> Single:
        # 外轮廓(正形)
        geo = shapely.Polygon(shell=self.geo.exterior)
        return Single.SIMPLE(geo=geo)

    @property
    def inner(self) -> Multi:
        # 内轮廓(负形)
        inners = [shapely.Polygon(shell=inner) for inner in self.geo.interiors]
        geo = shapely.MultiPolygon(polygons=inners)
        if geo.is_empty:
            return Shape.EMPTY
        return Multi.SIMPLE(geo=geo)

    def sep_in(self) -> Tuple[Single, Multi]:
        # 内分解
        return self.outer, self.inner

    def sep_out(self) -> List[Single]:
        # 外分解
        return [self]

    def sep_p(self) -> Tuple[
        List[Tuple[float, float]],
        List[List[Tuple[float, float]]]
    ]:
        # 点分解
        outer = list(self.geo.exterior.coords)
        inners = [list(inner.coords) for inner in self.geo.interiors]
        return outer, inners

    @property
    def cls(self) -> type:
        return ComplexPolygon


Single.COMPLEX = ComplexPolygon
