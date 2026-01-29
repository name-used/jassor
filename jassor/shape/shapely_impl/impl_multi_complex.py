import traceback
from typing import List, Tuple, Iterable
import sys
import shapely
from shapely.geometry.base import BaseGeometry

from .definition import Shape, Single, Multi, NoParametersException, CoordinatesNotLegalException
from .impl_base import Base
from .normalizer import deintersect
from shapely.ops import unary_union


class MultiComplexPolygon(Base, Multi):
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
            outers: List[List[Tuple[float, float]]] = None,
            inners: List[List[Tuple[float, float]]] = None,
            adjacencies: List[int] = None,

            geo: BaseGeometry = None,

            singles: Iterable[Shape] = None,

            from_p: Tuple[
                List[List[Tuple[float, float]]],    # outers
                List[List[Tuple[float, float]]],    # inners
                List[int],    # adjacencies
            ] = None,
            reverse: bool = False,
    ):
        if geo is not None:
            assert isinstance(geo, shapely.MultiPolygon), 'geo 必须是 MultiPolygon'
        elif singles is not None:
            assert not any(single.reversed for single in singles), '创建 MultiPolygon 时只能采用正形描述'
            geoms = []
            for single in singles:
                if not single: continue
                if isinstance(single, Single):
                    geoms.append(single.geo)
                elif isinstance(single, Multi):
                    geoms.extend(geo for geo in single.geo.geoms if isinstance(geo, shapely.Polygon))
            geo = shapely.MultiPolygon(polygons=geoms)
        elif from_p is not None:
            outers, inners, adjacencies = from_p
            inners = inners or []
            adjacencies = adjacencies or []
            coords = [(outer, []) for outer in outers]
            for inner, adjacency in zip(inners, adjacencies):
                coords[adjacency][1].append(inner)
            coords = [
                (outer, [inner for j, inner in enumerate(inners) if adjacencies[j] == i])
                for i, outer in enumerate(outers)
            ]
            geo = shapely.MultiPolygon(polygons=coords)
        elif outers is not None:
            inners = inners or []
            adjacencies = adjacencies or []
            coords_list = [(outer, []) for outer in outers]
            for inner, adjacency in zip(inners, adjacencies):
                if not(0 <= adjacency < len(coords_list)): continue
                coords_list[adjacency][1].append(inner)

            legal_coords_list = []
            for outer, inners in coords_list:
                outers = deintersect(outer)
                inners = sum([deintersect(inner) for inner in inners], [])
                if len(outers) == 0:
                    # 通常是因为轮廓点数不达标，直接报错就行
                    raise CoordinatesNotLegalException(f'creating multi polygon with one outer=={outers}')
                if len(outers) > 1:
                    # 单一轮廓修复后变成多个轮廓，说明轮廓存在自相交问题，此时需拆分外轮廓，并按配位关系重组内轮廓
                    sys.stderr.write(f'creating multi polygon found self-intersect coord=={outer}\n')
                    polygons = [shapely.Polygon(shell=outer, holes=[]) for outer in outers]
                    coords = [(polygon.exterior.coords, [inner for inner in inners if not polygon.disjoint(shapely.LineString(inner))]) for polygon in polygons]
                else:
                    polygon = shapely.Polygon(shell=outers[0], holes=[])
                    coords = [(polygon.exterior.coords, [inner for inner in inners if not polygon.disjoint(shapely.LineString(inner))])]
                legal_coords_list.extend(coords)

            # 对用户输入进行检查和修复
            geo = shapely.MultiPolygon(polygons=legal_coords_list)
            try:
                geo = unary_union(geo)
            except Exception as e:
                sys.stderr.write(f'geometry invalid caused by {e}\n')
            geo = geo.buffer(0)

            if geo.is_empty:
                # geo 是空，这种没办法，只能报错处理
                raise CoordinatesNotLegalException(f'creating single polygon with geo=={type(geo)}, pls check outer&inners:{outers}-{inners}')
            elif isinstance(geo, shapely.Polygon):
                # 如果 geo 是单个图形，那为了接口对齐，我也依然只能把它搞成 multi 的格式
                geo = shapely.MultiPolygon(polygons=[geo])
        else:
            # 没有任何参数的话，要报个错
            raise NoParametersException(f'Any of such parameters have to be provided: (outer, *inners), geo, single, from_p')

        super().__init__(geo=geo, reverse=reverse)

    @property
    def outer(self) -> Multi:
        # 外轮廓(正形)
        outer_geos = [shapely.Polygon(g.exterior.coords) for g in self.geo.geoms]
        geo = shapely.MultiPolygon(outer_geos)
        return Multi.SIMPLE(geo=geo)

    @property
    def inner(self) -> Multi:
        # 内轮廓(负形)
        inner_boundaries = [list(g.interiors) for g in self.geo.geoms]
        inner_boundaries = sum(inner_boundaries, [])
        geos = [shapely.Polygon(b.coords) for b in inner_boundaries]
        geo = shapely.MultiPolygon(polygons=geos)
        return Multi.SIMPLE(geo=geo)

    def sep_in(self) -> Tuple[Multi, Multi]:
        # 内分解
        return self.outer, self.inner

    def sep_out(self) -> List[Single]:
        # 外分解
        return [Single.COMPLEX(geo=g) for g in self.geo.geoms]

    def sep_p(self) -> Tuple[
        List[List[Tuple[int, int]]],
        List[List[Tuple[int, int]]],
        List[int]
    ]:
        # 点分解
        singles = [Single.COMPLEX(geo=g) for g in self.geo.geoms]
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
        return MultiComplexPolygon


Multi.COMPLEX = MultiComplexPolygon
