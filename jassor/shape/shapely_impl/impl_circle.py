from typing import List, Tuple

import math
from shapely.geometry.base import BaseGeometry

from .definition import Single
from .impl_single_simple import SimplePolygon


class Circle(SimplePolygon):
    """
    单-圆形，仅为了方便区域的创建，操作与凸形状完全一致
    实际存储时用的也是多边形，并不会真正创建一个圆
    """
    
    __slots__ = ()

    def __init__(
            self, x: float = 0, y: float = 0, r: float = 0, num: int = 100,
            geo: BaseGeometry = None,
            from_p: List[Tuple[int, int]] = None,
            reverse: bool = False,
    ):
        if geo is not None or from_p is not None:
            outer = None
        else:
            base_directs = [2 * math.pi / num * i for i in range(num)]
            base_points = [(math.cos(d), math.sin(d)) for d in base_directs]
            outer = [(x + p * r, y + q * r) for p, q in base_points]
        super().__init__(outer, geo=geo, from_p=from_p, reverse=reverse)

    @property
    def cls(self) -> type:
        return Circle


Single.CIRCLE = Circle
