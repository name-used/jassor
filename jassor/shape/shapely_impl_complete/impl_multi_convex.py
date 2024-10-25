from .definition import Multi
from .impl_multi_simple import SimpleMultiPolygon


class ConvexMultiPolygon(SimpleMultiPolygon):
    """
    多-凸多边形, 对凸性不做校验, 与 多-单连通多边形 完全一致
    仅作为类型标识符存在
    """

    @property
    def cls(self) -> type:
        return ConvexMultiPolygon


Multi.CONVEX = ConvexMultiPolygon
