from shapely.geometry.base import BaseGeometry

from .definition import Single
from .impl_single_simple import SimplePolygon


class ConvexPolygon(SimplePolygon):
    """
    单-凸多边形, 对凸性不做校验, 与 单-单连通多边形 完全一致
    仅作为类型标识符存在
    """

    @property
    def cls(self) -> type:
        return ConvexPolygon


Single.CONVEX = ConvexPolygon


class Region(ConvexPolygon):
    """
    单-矩形，仅为了方便区域的创建，操作与凸形状完全一致
    仅作为类型标识符存在
    """

    def __init__(
            self, left: float = 0, up: float = 0, right: float = 0, down: float = 0,
            geo: BaseGeometry = None
    ):
        if geo is not None:
            super().__init__(geo=geo)
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
