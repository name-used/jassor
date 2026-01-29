from typing import List, Tuple, Iterable
import sys
import shapely
from shapely.geometry.base import BaseGeometry

from .definition import Shape, Single, Multi, NoParametersException, CoordinatesNotLegalException, number
from .impl_multi_complex import MultiComplexPolygon
from .normalizer import deintersect
from shapely.ops import unary_union


class MultiSimplePolygon(MultiComplexPolygon):
    """
    多-单连通多边形, 创建方式有四:
    1. 指定 geo
    2. 指定 Multi
    3. 指定 Single 数组
    4. 指定 outers
    遵循逆序优先规则
    """

    __slots__ = ()

    def __init__(
            self,
            outers: List[List[Tuple[number, number]]] = None,
            geo: BaseGeometry = None,
            singles: Iterable[Shape] = None,
            from_p: List[List[Tuple[number, number]]] = None,
            reverse: bool = False,
    ):
        if geo is not None:
            assert isinstance(geo, shapely.MultiPolygon), 'geo 必须是 MultiPolygon'
            assert all(g.boundary.geom_type.upper() == 'LINESTRING' for g in geo.geoms), 'geo 必须是单连通的'
        elif singles is not None:
            assert all(isinstance(single, (Single.SIMPLE, Multi.SIMPLE)) for single in singles if single), 'shapes 必须由 SIMPLE（单连通） 图像构成'
        elif from_p is not None:
            geo = shapely.MultiPolygon(polygons=[(outer, []) for outer in outers])
        elif from_p is not None:
            geo = shapely.MultiPolygon(polygons=[(outer, []) for outer in from_p])
        elif outers is not None:
            _outers = sum([deintersect(outer) for outer in outers], [])
            # 对用户输入进行检查和修复
            geo = shapely.MultiPolygon(polygons=[(outer, []) for outer in _outers])
            try:
                geo = unary_union(geo)
            except Exception as e:
                sys.stderr.write(f'geometry invalid caused by {e}\n')
            geo = geo.buffer(0)

            if geo.is_empty:
                # geo 是空，这种没办法，只能报错处理
                raise CoordinatesNotLegalException(f'creating single polygon with geo=={type(geo)}, pls check outers:{outers}')
            elif isinstance(geo, shapely.Polygon):
                # 如果 geo 是单个图形，那为了接口对齐，我也依然只能把它搞成 multi 的格式
                geo = shapely.MultiPolygon(polygons=[geo])
            # unary_union 和 buffer 之后可能会再次出现洞洞之类的，所以再取一遍外轮廓
            # outer_geos = [shapely.Polygon(g.exterior.coords) for g in geo.geoms]
            geo = shapely.MultiPolygon([(g.exterior.coords, []) for g in geo.geoms])
        else:
            # 没有任何参数的话，要报个错
            raise NoParametersException(f'Any of such parameters have to be provided: (outer, *inners), geo, single, from_p')

        super().__init__(outers=None, geo=geo, singles=singles, reverse=reverse)

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
        return Multi.SIMPLE(geo=self.geo)

    @property
    def inner(self) -> Shape.EMPTY:
        # 内轮廓(负形)
        return Shape.EMPTY

    def sep_in(self) -> Tuple[Multi, Shape.EMPTY]:
        # 内分解
        # 逐层分解 (规避由 shapely 的任意性引起的荒诞错误)
        return self, Shape.EMPTY

    def sep_out(self) -> List[Single]:
        # 外分解
        singles = [Single.SIMPLE(geo=g) for g in self.geo.geoms if isinstance(g, shapely.Polygon)]
        singles = [s for s in singles if s.is_valid()]
        return singles

    def sep_p(self) -> List[List[Tuple[int, int]]]:
        # 点分解
        # 逐层分解 (规避由 shapely 任意性引起的荒诞错误)
        singles = [Single.SIMPLE(geo=g) for g in self.geo.geoms if isinstance(g, shapely.Polygon)]
        singles = [s for s in singles if s.is_valid()]
        return [s.sep_p() for s in singles if s.is_valid()]

    @property
    def cls(self) -> type:
        return MultiSimplePolygon


Multi.SIMPLE = MultiSimplePolygon
