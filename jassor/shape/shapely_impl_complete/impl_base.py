import io
import json
import pickle
from abc import ABC
from typing import Tuple, Union, Iterable
from shapely.geometry.base import BaseGeometry
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

    def is_joint(self, other: Shape) -> bool:
        # EMPT 和 FULL 不属于 Base，不会调用此方法，其判别在自己的逻辑内进行即可
        if other is Shape.EMPTY or other is Shape.FULL: return other.is_joint(self)
        if not self.reversed and not other.reversed:        # 对正常图形来说，直接调库
            return self.geo.intersects(other.geo)
        if self.reversed and other.reversed:                # 两个反形必然相交，因为无穷远处总有一个元素同时属于二者
            return True
        if not self.reversed and other.reversed:            # 一正一反的情况下，需要判断是否反形完全涵盖正形
            return not other.geo.contains(self.geo)
        if self.reversed and not other.reversed:            # 一正一反的情况下，需要判断是否反形完全涵盖正形
            return not self.geo.contains(other.geo)

    def if_contain(self, other: Shape) -> bool:
        # EMPT 和 FULL 不属于 Base，不会调用此方法，其判别在自己的逻辑内进行即可
        if other is Shape.EMPTY or other is Shape.FULL: return other.is_joint(self)
        if not self.reversed and not other.reversed:        # 对正常图形来说，直接调库
            return self.geo.contains(other.geo)
        if self.reversed and other.reversed:                # 两个反形的包含关系刚好调过来
            return other.geo.contains(self.geo)
        if not self.reversed and other.reversed:            # 正形不可能包含反形
            return False
        if self.reversed and not other.reversed:            # 反形的 geo 与正形完全不相交的情况下即意味着包含
            return not self.geo.intersects(other.geo)

    # 这一批运算会改变轮廓类型
    def inter(self, other: Shape) -> Shape:
        # EMPT 和 FULL 不属于 Base，不会调用此方法，其判别在自己的逻辑内进行即可
        if other is Shape.EMPTY or other is Shape.FULL: return other.inter(self)
        # 依据 reverse 标志决定真实运算
        if not self.reversed and not other.reversed:        # 正 + 正 -> 正常运算 - 交         A & B = A & B
            return F.inter(self, other, reverse=False)
        if self.reversed and other.reversed:                # 反 + 反 -> 镜像运算 - 反(并)     ~A & ~B = ~(A | B)
            return F.union(self, other, reverse=True)
        if not self.reversed and other.reversed:            # 正 + 反 -> 正斜运算 - 我移除它    A & ~B = A >> B
            return F.remove(self, other, reverse=False)
        if self.reversed and not other.reversed:            # 反 + 正 -> 反斜运算 - 它移除我    ~A & B = B >> A
            return F.remove(other, self, reverse=False)

    def union(self, other: Shape) -> Shape:
        # EMPT 和 FULL 不属于 Base，不会调用此方法，其判别在自己的逻辑内进行即可
        if other is Shape.EMPTY or other is Shape.FULL: return other.union(self)
        # 依据 reverse 标志决定真实运算
        if not self.reversed and not other.reversed:        # 正 + 正 -> 正常运算 - 并             A | B = A | B
            return F.union(self, other, reverse=False)
        if self.reversed and other.reversed:                # 反 + 反 -> 镜像运算 - 反(交)         ~A | ~B = ~(A & B)
            return F.inter(self, other, reverse=True)
        if not self.reversed and other.reversed:            # 正 + 反 -> 正斜运算 - 反(它移除我)    A | ~B = ~(~A & B) = ~(B >> A)
            return F.remove(other, self, reverse=True)
        if self.reversed and not other.reversed:            # 反 + 正 -> 反斜运算 - 反(我移除它)    ~A | B = ~(A & ~B) = ~(A >> B)
            return F.remove(self, other, reverse=True)

    def diff(self, other: Shape) -> Shape:
        # EMPT 和 FULL 不属于 Base，不会调用此方法，其判别在自己的逻辑内进行即可
        if other is Shape.EMPTY or other is Shape.FULL: return other.diff(self)
        # 依据 reverse 标志决定真实运算
        if not self.reversed and not other.reversed:        # 正 + 正 -> 正常运算 - 异         A ^ B = (A & ~B) | (~A & B) = A ^ B
            return F.diff(self, other, reverse=False)
        if self.reversed and other.reversed:                # 反 + 反 -> 镜像运算 - 异         ~A ^ ~B = (~A & B) | (A & ~B) = A ^ B
            return F.diff(self, other, reverse=False)
        if not self.reversed and other.reversed:            # 正 + 反 -> 正斜运算 - 反(异)      A ^ ~B = (A & B) | (~A & ~B) = (A&B) | ~(A|B) = ~[~(A&B) & (A|B)] = ~[(A|B) >> (A&B)] = ~(A ^ B)
            return F.remove(other, self, reverse=True)
        if self.reversed and not other.reversed:            # 反 + 正 -> 反斜运算 - 反(异)      ~A ^ B = A ^ ~B = ~(A ^ B)
            return F.remove(self, other, reverse=True)

    def remove(self, other: Shape) -> Shape:
        # EMPT 和 FULL 不属于 Base，不会调用此方法，其判别在自己的逻辑内进行即可
        if other is Shape.EMPTY or other is Shape.FULL: return other.remove(self)
        # 依据 reverse 标志决定真实运算
        if not self.reversed and not other.reversed:        # 正 + 正 -> 正常运算 - 我移除它      A >> B = (A & ~B) = A >> B
            return F.remove(self, other, reverse=False)
        if self.reversed and other.reversed:                # 反 + 反 -> 镜像运算 - 它移除我      ~A >> ~B = (~A & B) = B >> A
            return F.remove(other, self, reverse=False)
        if not self.reversed and other.reversed:            # 正 + 反 -> 正斜运算 - 交           A >> ~B = (A & B) = A & B
            return F.inter(self, other, reverse=False)
        if self.reversed and not other.reversed:            # 反 + 正 -> 反斜运算 - 反(并)       ~A >> B = (~A & ~B) = ~(A|B)
            return F.union(self, other, reverse=True)

    def merge(self, others: Iterable[Shape]) -> Shape:
        # 排除与自身不相交的
        joins = [other for other in others if self.is_joint(other)]
        # 检查有没有 Full, 如果有, 直接返回 Full
        if any((other is Shape.FULL) for other in joins): return Shape.FULL
        # 将自己也加进去
        joins.append(self)
        # 相交的图形将正形反形分离开
        pos_shapes = [other for other in joins if not other.reversed]
        neg_shapes = [other for other in joins if other.reversed]
        # 正形参与 union 运算
        pos_shape = F.union(*pos_shapes, reverse=False)
        # 反形参与 inter 运算
        neg_shape = F.inter(*neg_shapes, reverse=True)
        # 二者之和即为所求
        return pos_shape.union(neg_shape)

    def simplify(self, tolerance: float = 0.5) -> Shape:
        geo = self.geo.simplify(tolerance=tolerance, preserve_topology=True)
        return F.norm_multi(geo, reverse=self.reversed)

    def smooth(self, distance: float = 3) -> Shape:
        distance = -distance if self.reversed else distance
        geo = self.geo.buffer(-distance).buffer(distance)
        return F.norm_multi(geo, reverse=self.reversed)

    def buffer(self, distance: float = 3) -> Shape:
        distance = -distance if self.reversed else distance
        geo = self.geo.buffer(distance=distance)
        return F.norm_multi(geo, reverse=self.reversed)

    def standard(self) -> Multi:
        return F.norm_multi(self.geo, reverse=self.reversed)

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
