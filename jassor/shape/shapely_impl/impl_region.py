from typing import Tuple

from shapely.geometry.base import BaseGeometry

from .definition import Single
from .impl_single_simple import SimplePolygon


class Region(SimplePolygon):
    """
    单-矩形，仅为了方便区域的创建，操作与凸形状完全一致
    仅作为类型标识符存在
    """

    __slots__ = ()

    def __init__(
            self, left: float = 0, up: float = 0, right: float = 0, down: float = 0,
            geo: BaseGeometry = None,
            from_p: Tuple[float, float, float, float] = None,
            reverse: bool = False,
    ):
        if geo is not None:
            outer = None
        else:
            if from_p is not None:
                left, up, right, down = from_p
            p1 = (left, up)
            p2 = (left, down)
            p3 = (right, down)
            p4 = (right, up)
            outer = [p1, p2, p3, p4]
        super().__init__(outer, geo=geo, from_p=None, reverse=reverse)

    def sep_p(self) -> Tuple[float, float, float, float]:
        return self.geo.bounds

    @property
    def cls(self) -> type:
        return Region


Single.REGION = Region
