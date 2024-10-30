import io
import json
import pickle
from abc import ABC
from typing import Tuple, Union, Optional
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry
from shapely.geometry.geo import MultiPolygon as StandardMultiPolygon
from shapely.geometry.geo import Polygon as StandardPolygon
from shapely.ops import unary_union
import shapely.affinity as A

from .definition import Shape, Single, Multi
import functional as F


Position = Union[str, complex, Tuple[float, float]]


class Base(Shape, ABC):

    def __init__(self, geo: BaseGeometry, reverse: bool = False):
        self._geo = geo
        self._reversed = reverse

    # 这一批运算不改变轮廓类型
    def comp(self) -> None:
        self._reversed = not self._reversed

    def offset(self, vector: Position) -> Shape:
        if isinstance(vector, str):
            assert vector == 'origin', '仅支持 "origin" 作为入参'  # 平移图像直至中心点为原点
            x, y = self.center
            x = -x
            y = -y
        else:
            x, y = (vector.real, vector.imag) if isinstance(vector, complex) else vector
        self._geo = A.translate(self._geo, x, y)
        return self

    def scale(self, ratio: Union[float, complex, tuple], origin: Position = 0j) -> Shape:
        # 缩放比例支持
        if isinstance(ratio, (float, int)):
            x_fact = y_fact = ratio
        elif isinstance(ratio, complex):
            x_fact = ratio.real
            y_fact = ratio.imag
        else:
            x_fact, y_fact = ratio
        # 原点支持
        if isinstance(origin, complex):
            origin = (origin.real, origin.imag)
        elif isinstance(origin, str):
            assert origin == 'center', '仅支持 "center" 作为入参'
        self._geo = A.scale(self._geo, xfact=x_fact, yfact=y_fact, zfact=0, origin=origin)
        return self

    def rotate(self, degree: float, origin: Union[str, Position] = 0j) -> Shape:
        # 注意注意：此处的 degree 是角度制
        # 原点支持
        if isinstance(origin, complex):
            origin = (origin.real, origin.imag)
        elif isinstance(origin, str):
            assert origin == 'center', '仅支持 "center" 作为入参'
        self._geo = A.rotate(self._geo, angle=degree, origin=origin)
        return self

    def flip_x(self, x0: float) -> Shape:
        self._geo = A.scale(self._geo, xfact=-1, yfact=1, zfact=0, origin=(x0, 0))
        return self

    def flip_y(self, y0: float) -> Shape:
        self._geo = A.scale(self._geo, xfact=1, yfact=-1, zfact=0, origin=(0, y0))
        return self

    def flip(self, degree: float, origin: Position) -> Shape:
        # 直接两次旋转一次对称来做
        if isinstance(origin, str):
            assert origin == 'center', '仅支持 "center" 作为入参'
            x, y = self.center
        else:
            x, y = (origin.real, origin.imag) if isinstance(origin, complex) else origin
        self.rotate(degree=-degree, origin=(x, y))
        self.flip_y(y0=y)
        self.rotate(degree=degree, origin=(x, y))
        return self

    # 这一批运算会改变轮廓类型
    def inter(self, other: Shape) -> Shape:
        # 依据 reverse 标志决定真实运算
        if not self.reversed and not other.reversed:        # 正 + 正 -> 正常运算 - 交         A & B = A & B
            return F.inter(self, other, reverse=False)
        if self.reversed and other.reversed:                # 反 + 反 -> 镜像运算 - 并         ~A & ~B = ~(A | B)
            return F.union(self, other, reverse=True)
        if not self.reversed and other.reversed:            # 正 + 反 -> 正斜运算 - 我移除它    A & ~B = A >> B
            return F.remove(self, other, reverse=False)
        if self.reversed and not other.reversed:            # 反 + 正 -> 反斜运算 - 它移除我    ~A & B = B >> A
            return F.remove(other, self, reverse=False)

    def union(self, other: Shape) -> Shape:
        # 依据 reverse 标志决定真实运算
        if not self.reversed and not other.reversed:        # 正 + 正 -> 正常运算 - 并             A | B = A | B
            return F.union(self, other, reverse=False)
        if self.reversed and other.reversed:                # 反 + 反 -> 镜像运算 - 交             ~A | ~B = ~(A & B)
            return F.inter(self, other, reverse=True)
        if not self.reversed and other.reversed:            # 正 + 反 -> 正斜运算 - 反(它移除我)    A | ~B = ~(~A & B) = ~(B >> A)
            return F.remove(other, self, reverse=True)
        if self.reversed and not other.reversed:            # 反 + 正 -> 反斜运算 - 反(我移除它)    ~A | B = ~(A & ~B) = ~(A >> B)
            return F.remove(self, other, reverse=True)

    def diff(self, other: Shape) -> Shape:
        # 依据 reverse 标志决定真实运算
        if not self.reversed and not other.reversed:        # 正 + 正 -> 正常运算 - 异
            return F.diff(self, other, reverse=False)
        if self.reversed and other.reversed:                # 反 + 反 -> 镜像运算 - 异
            return F.diff(self, other, reverse=False)
        if not self.reversed and other.reversed:            # 正 + 反 -> 正斜运算 - 反(异)
            return F.remove(other, self, reverse=True)
        if self.reversed and not other.reversed:            # 反 + 正 -> 反斜运算 - 反(异)
            return F.remove(self, other, reverse=True)

    def remove(self, other: Shape) -> Shape:
        if not other: return self.__norm_multi__(self._geo)
        geo = self._geo.difference(other.geo)
        return self.__norm_multi__(geo)

    def merge(self, other: Shape) -> Shape:
        # 合集运算
        if not other: return Multi.asComplex(self)
        geo = self.geo
        singles = other.sep_out()
        geos = [s.geo for s in singles if not geo.disjoint(s.geo)]
        for g in geos:
            geo = geo.union(g)
        multi = self.__norm_multi__(geo)
        return MultiComplexPolygon(multi=multi)

    def merge(self, other: Shape) -> Shape:
        # 合集运算
        # 这里不能用 copy，因为该方法会被 simple、region、circle 等方法继承，而 merge 是一个运算方法，运算方法的返回值需要保证结果一致性
        if not other: return Single.asComplex(self)
        geo = self.geo
        singles = other.sep_out()
        # 接下来开始考虑 reverse 问题了
        if self.reversed and other.reversed:
            # 两个都反转，必定相交，因此无需判断相交性
            # 由于 geo 并不参与反转运算，其所表示的都是“外部”，两个轮廓的融合相当于取并，此处取反，并变交
            for g in [s.geo for s in singles]:
                geo = geo.intersection(g)
                geo = self._norm_single(geo)


        elif not self.reversed and other.reversed:
            # 两个都不反转，
            geos = [s.geo for s in singles if not geo.disjoint(s.geo)]
            for g in geos:
                geo = geo.union(g)
            single = self.__norm_single__(geo)
            return Single.asComplex(shape=single)


    def simplify(self, tolerance: float = 0.5) -> Shape:
        """
        In project: lung_area_seg, there is a image part-id:
            "4|TCGA-NK-A5CR-01Z-00-DX1.A7C57B30-E2C6-4A23-AE71-7E4D7714F8EA"
        that makes error in simplify function.
        I found that might be caused by 'preserve_topology=False' which uses the following algorithm --- fast but wrong:
            David H.Douglas && Thomas K.Peucker
        to simplify instead of normal-topology-friendly algorithm --- slow but stable.
        """
        geo = self._geo.simplify(tolerance=tolerance, preserve_topology=True)
        return self._norm_multi(geo)

    def smooth(self, distance: float = 3) -> Shape:
        geo = self._geo._buffer(-distance)._buffer(distance)
        return self.__norm_multi__(geo)

    def buffer(self, distance: float = 3) -> Shape:
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
        return self.cls(geo=self._geo, reverse=self.reversed)

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
