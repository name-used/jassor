from typing import List, Tuple

from shapely.geometry.base import BaseGeometry

from .definition import Single
from .impl_single_simple import SimplePolygon


class Region(SimplePolygon):
    """
    单-矩形，仅为了方便区域的创建，操作与凸形状完全一致
    仅作为类型标识符存在
    """
    def __init__(
            self, left: float = 0, up: float = 0, right: float = 0, down: float = 0,
            from_p: List[Tuple[int, int]] = None,
            geo: BaseGeometry = None,
    ):
        if geo is not None:
            super().__init__(geo=geo)
        elif from_p is not None:
            super().__init__(outer=from_p)
        else:
            p1 = (left, up)
            p2 = (left, down)
            p3 = (right, down)
            p4 = (right, up)
            super().__init__(outer=[p1, p2, p3, p4])

    @property
    def cls(self) -> type:
        return Region


Single.REGION = Region
