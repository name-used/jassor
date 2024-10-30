from typing import List, Tuple, Iterable

import shapely
from shapely.geometry.base import BaseGeometry

from .definition import Shape, Single, Multi
from .impl_base import Base


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
            outers: List[Tuple[float, float]] = None,
            inners: List[Tuple[float, float]] = None,
            adjacencies: List[int] = None,

            geo: BaseGeometry = None,

            shapes: Iterable[Shape] = None,

            from_p: Tuple[
                List[List[Tuple[float, float]]],    # outers
                List[List[Tuple[float, float]]],    # inners
                List[List[Tuple[float, float]]],    # adjacencies
            ] = None,
            reverse: bool = False,
    ):
        if geo is not None:
            assert isinstance(geo, shapely.MultiPolygon), 'geo 必须是 MultiPolygon'
        elif shapes is not None:
            assert not any(shape.reversed() for shape in shapes), '创建 MultiPolygon 时只能采用正形描述'
            geoms = []
            for shape in shapes:
                if not shape: continue
                if isinstance(shape, Single):
                    geoms.append(shape.geo)
                elif isinstance(shape, Multi):
                    geoms.extend(geo for geo in shape.geo.geoms if isinstance(geo, shapely.Polygon))
            geo = shapely.MultiPolygon(polygons=geoms)
        else:
            if from_p is not None:
                outers, inners, adjacencies = from_p
            if outers is not None:
                if inners is None and adjacencies is None:
                    coords = [(outer, []) for outer in outers]
                else:
                    assert inners is not None and adjacencies is not None and len(inners) == len(adjacencies), '孔洞未对齐'
                    coords = [
                        (outer, [inner for j, inner in enumerate(inners) if adjacencies[j] == i])
                        for i, outer in enumerate(outers)
                    ]
                geo = shapely.MultiPolygon(polygons=coords)
            else:
                # 没有任何参数的话，就创建一个空对象
                geo = shapely.MultiPolygon()
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
