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

Position = Union[str, complex, Tuple[float, float]]


# 这一批运算会改变轮廓类型
def inter(self: Shape, other: Shape, reverse: bool) -> Shape:
    if not other: return Shape.EMPTY
    geo = self._geo.intersection(other.geo)
    return norm_multi(self, geo, reverse=reverse)


def union(self: Shape, other: Shape, reverse: bool) -> Shape:
    if not other: return self.__norm_multi__(self._geo)
    geo = self._geo.union(other.geo)
    return self.__norm_multi__(geo)


def merge(self: Shape, other: Shape, reverse: bool) -> Shape:
    # 合集运算
    if not other: return Multi.asComplex(self)
    geo = self.geo
    singles = other.sep_out()
    geos = [s.geo for s in singles if not geo.disjoint(s.geo)]
    for g in geos:
        geo = geo.union(g)
    multi = self.__norm_multi__(geo)
    return MultiComplexPolygon(multi=multi)

def merge(self: Shape, other: Shape, reverse: bool) -> Shape:
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


def diff(self: Shape, other: Shape, reverse: bool) -> Shape:
    if not other: return self.__norm_multi__(self._geo)
    geo = self._geo.symmetric_difference(other.geo)
    return self.__norm_multi__(geo)


def remove(self: Shape, other: Shape, reverse: bool) -> Shape:
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
    return self._norm_multi(geo)

def smooth(self, distance: float = 3) -> Multi:
    geo = self._geo._buffer(-distance)._buffer(distance)
    return self.__norm_multi__(geo)

def _buffer(self, distance: float = 3) -> Multi:
    geo = self._geo.buffer(distance)
    return self.__norm_multi__(geo)

def standard(self) -> Multi:
    geo = unary_union(self._geo)
    return self.__norm_multi__(geo)


def norm_single(geo: BaseGeometry) -> Multi:
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


def norm_multi(geo: BaseGeometry) -> Multi:
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
