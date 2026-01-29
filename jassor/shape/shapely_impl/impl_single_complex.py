import sys
from typing import List, Tuple

import shapely
from shapely.geometry.base import BaseGeometry

from .definition import Shape, Single, Multi, CoordinatesNotLegalException, NoParametersException
from .impl_base import Base
from . import functional as F
from .normalizer import deintersect
from shapely.ops import unary_union


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
            inners: List[List[Tuple[float, float]]] = None,
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
            coords = deintersect(outer)
            if len(coords) == 0:
                # 通常是因为轮廓点数不达标，直接报错就行
                raise CoordinatesNotLegalException(f'creating single polygon with outer=={outer}')
            if len(coords) > 1:
                # 单一轮廓修复后变成多个轮廓，说明轮廓存在自相交问题，此时只保留最大轮廓
                polygons = [shapely.Polygon(shell=coord, holes=[]) for coord in coords]
                polygons.sort(key=lambda poly: poly.area, reverse=True)
                sys.stderr.write(f'creating single polygon with multi-polygon drop coords with area {[poly.area for poly in polygons]}\n')
                polygon = polygons[0]
            else:
                polygon = shapely.Polygon(shell=coords[0], holes=[])
            # 然后处理内轮廓
            inners = sum([deintersect(inner) for inner in inners], [])
            inners = [inner for inner in inners if not polygon.disjoint(shapely.LineString(inner))]

            # inners_group = unary_union(shapely.MultiPolygon(polygons=[shapely.Polygon(shell=inner, holes=[]) for inner in inners_group]))
            geo = shapely.Polygon(shell=polygon.exterior.coords, holes=inners)
            try:
                geo = unary_union(geo)
            except Exception as e:
                sys.stderr.write(f'geometry invalid caused by {e}\n')
            geo = geo.buffer(0)
            if geo.is_empty:
                # 此时存在两种可能性，一种是空，这种没办法，只能报错处理
                raise CoordinatesNotLegalException(f'creating single polygon with geo=={type(geo)}, pls check outer&inners:{outer}-{inners}')
            # 如果图案断开，只取面积最大的（因为我们断言这是一个简单单连通图案）
            if isinstance(geo, shapely.MultiPolygon):
                sys.stderr.write(f'creating single polygon with multi-polygon drop coords with area {sorted([g.area for g in geo.geoms], reverse=True)}\n')
                geo = max(geo.geoms, key=lambda g: g.area)
            elif not isinstance(geo, shapely.Polygon):
                raise CoordinatesNotLegalException(f'wrong geometry type {type(geo)}, pls check outer&inners:{outer}-{inners}')
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
