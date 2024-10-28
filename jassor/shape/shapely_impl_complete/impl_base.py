import io
import json
import pickle
from abc import ABC
from typing import Tuple, Union, TypeVar
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry
from shapely.geometry.geo import MultiPolygon as StandardMultiPolygon
from shapely.geometry.geo import Polygon as StandardPolygon
from shapely.ops import unary_union
import shapely.affinity as A

from .definition import Shape, Single, Multi


class Base(Shape, ABC):

    def __init__(self, geo: BaseGeometry, reverse: bool = False):
        self._geo = geo
        self._reversed = reverse

    def offset(self, pos: Union[complex, Tuple[float, float]]) -> Shape:
        x, y = (pos.real, pos.imag) if isinstance(pos, complex) else pos
        self._geo = A.translate(self._geo, x, y)
        return self

    def scale(self, ratio: Union[float, tuple]) -> Shape:
        if isinstance(ratio, (float, int)):
            x_fact = y_fact = ratio
        else:
            x_fact, y_fact = ratio
        self._geo = A.scale(self._geo, xfact=x_fact, yfact=y_fact, zfact=0, origin=(0, 0, 0))
        return self

    def rotate(self, degree: float) -> Shape:
        self._geo = A.rotate(self._geo, angle=degree, origin=(0, 0, 0))
        return self

    def flip_x(self, intercept_x: float) -> Shape:
        self._geo = A.scale(self._geo, xfact=-1, yfact=1, zfact=0, origin=(intercept_x, 0, 0))
        return self

    def flip_y(self, intercept_y: float) -> Shape:
        self._geo = A.scale(self._geo, xfact=1, yfact=-1, zfact=0, origin=(0, intercept_y, 0))
        return self

    def flip(self, intercept_x: float, intercept_y: float) -> Shape:
        raise NotImplemented('not yet')

    def inter(self, other: Shape) -> Multi:
        if not other: return Shape.EMPTY
        geo = self._geo.intersection(other.geo)
        return self.__norm_multi__(geo)

    def union(self, other: Shape) -> Multi:
        if not other: return self.__norm_multi__(self._geo)
        geo = self._geo.union(other.geo)
        return self.__norm_multi__(geo)

    def diff(self, other: Shape) -> Multi:
        if not other: return self.__norm_multi__(self._geo)
        geo = self._geo.symmetric_difference(other.geo)
        return self.__norm_multi__(geo)

    def remove(self, other: Shape) -> Multi:
        if not other: return self.__norm_multi__(self._geo)
        geo = self._geo.difference(other.geo)
        return self.__norm_multi__(geo)

    def simplify(self, tolerance: float = 0.5) -> Multi:
        """
        In project: lung_area_seg, there is a image part-id:
            "4|TCGA-NK-A5CR-01Z-00-DX1.A7C57B30-E2C6-4A23-AE71-7E4D7714F8EA"
        that makes error in simplify function.
        I found that might be caused by 'preserve_topology=False' which uses the following algorithm --- fast but wrong:
            David H.Douglas && Thomas K.Peucker
        to simplify instead of normal-topology-friendly algorithm --- slow but stable.
        """
        geo = self._geo.simplify(tolerance=tolerance, preserve_topology=True)
        return self.__norm_multi__(geo)

    def smooth(self, distance: float = 3) -> Multi:
        geo = self._geo.buffer(-distance).buffer(distance)
        return self.__norm_multi__(geo)

    def buffer(self, distance: float = 3) -> Multi:
        geo = self._geo.buffer(distance)
        return self.__norm_multi__(geo)

    def standard(self) -> Multi:
        geo = unary_union(self._geo)
        return self.__norm_multi__(geo)

    @property
    def convex(self) -> Single:
        geo = self._geo.convex_hull
        return Single.SIMPLE(geo=geo)

    @property
    def mini_rect(self) -> Single:
        geo = self._geo.minimum_rotated_rectangle
        return Single.SIMPLE(geo=geo)

    @property
    def region(self) -> Single:
        l, u, r, d = self._geo.bounds
        return Single.REGION(l, u, r, d)

    @property
    def center(self) -> Tuple[int, int]:
        return self._geo.centroid.coords[0]

    @property
    def area(self) -> float:
        return self._geo.area

    @property
    def perimeter(self) -> float:
        return self._geo.length

    @property
    def bounds(self) -> Tuple[int, int, int, int]:
        return self._geo.bounds

    @property
    def geo(self) -> BaseGeometry:
        return self._geo

    @property
    def cls(self) -> type:
        raise NotImplementedError

    def copy(self) -> Shape:
        return self.cls(geo=self._geo)

    def dumps(self) -> str:
        tp = self.cls().__name__
        rvs = self.reversed
        contour = self.sep_p()
        return f'{tp}\n{rvs}\n{json.dumps(contour)}'

    def dumpb(self, f: io.BufferedWriter):
        tp = self.cls().__name__
        rvs = self.reversed
        contour = self.sep_p()
        pickle.dump((tp, rvs, contour), f)

    @staticmethod
    def __norm_single__(geo: BaseGeometry) -> Multi:
        # 过滤 geo， 若 geo 不合法， 直接返回 EMPTY
        if not (geo is not None and geo.is_valid and not geo.is_empty and geo.area > 0):
            return Shape.EMPTY
        # 否则一律返回 Single （集合论运算的结果一律是 Multi）
        if isinstance(geo, StandardPolygon):
            # 单形升多形
            geo = StandardPolygon(geo)
        elif isinstance(geo, BaseMultipartGeometry):
            # 多部分形状若含且只含一个 Polygon，则可用
            polygons = [g for g in geo.geoms if isinstance(g, StandardPolygon)]
            if len(polygons) != 1:
                raise TypeError(f'geo 不合法！ {type(geo)}')
            geo = StandardPolygon(polygons[0])
        else:
            raise RuntimeError(f'鬼知道发生了什么, 快来处理bug: {type(geo)}')
        return Single.COMPLEX(geo=geo)

    @staticmethod
    def __norm_multi__(geo: BaseGeometry) -> Multi:
        # 过滤 geo， 若 geo 不合法， 直接返回 EMPTY
        if not (geo is not None and geo.is_valid and not geo.is_empty and geo.area > 0):
            return Shape.EMPTY
        # 否则一律返回 Multi （集合论运算的结果一律是 Multi）
        if isinstance(geo, StandardPolygon):
            # 单形升多形
            geo = StandardMultiPolygon([geo])
        elif isinstance(geo, BaseMultipartGeometry):
            # 多部分形状只保留 Polygon
            polygons = [g for g in geo.geoms if isinstance(g, StandardPolygon)]
            geo = StandardMultiPolygon(polygons)
        elif isinstance(geo, StandardMultiPolygon):
            # 多边形保留
            pass
        else:
            raise RuntimeError(f'鬼知道发生了什么, 快来处理bug: {type(geo)}')
        return Multi.COMPLEX(geo=geo)
