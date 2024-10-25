from abc import ABC
from shapely.geometry.base import BaseGeometry

from ..interface import Shape as Interface


class Shape(Interface, ABC):
    """
    Shape 是一切基于 shapely 库轮廓的超类
    """
    EMPTY = None
    FULL = None

    def __bool__(self) -> bool:
        return self != self.EMPTY

    # 以下为 shapely 专属
    def is_valid(self) -> bool:
        geo = self.geo
        return geo is not None and geo.is_valid and not geo.is_empty and geo.area > 0

    @property
    def geo(self) -> BaseGeometry:
        raise NotImplementedError

    def clean(self):
        raise NotImplementedError

    def is_joint(self, other) -> bool:
        if self.is_valid() and other.is_valid():
            return not self.geo.disjoint(other.geo)
        else:
            return False


class Single(Shape, ABC):
    # 凸形,单形,复形的定义
    REGION = None
    CONVEX = None
    SIMPLE = None
    COMPLEX = None

    @staticmethod
    def asSimple(shape: Shape) -> Shape:
        if not shape: return Shape.EMPTY
        assert isinstance(shape, Single), 'Multi 类型无法转换为 Single'
        return shape.outer

    @staticmethod
    def asComplex(shape: Shape) -> Shape:
        if not shape: return Shape.EMPTY
        assert isinstance(shape, Single), 'Multi 类型无法转换为 Single'
        return Single.COMPLEX(single=shape)

    def clean(self):
        # 单轮廓的清洗返回自身
        return self if self.is_valid() else Shape.EMPTY


class Multi(Shape, ABC):
    # 多凸形,多单形,多复形的定义
    CONVEX = None
    SIMPLE = None
    COMPLEX = None

    @staticmethod
    def asSimple(shape: Shape) -> Shape:
        if not shape: return Shape.EMPTY
        assert isinstance(shape, Multi), '将 Single 转换为 Multi 请直接创建指定类型'
        return shape.outer

    @staticmethod
    def asComplex(shape: Shape) -> Shape:
        if not shape: return Shape.EMPTY
        assert isinstance(shape, Multi), '将 Single 转换为 Multi 请直接创建指定类型'
        return Multi.COMPLEX(multi=shape)

    def clean(self):
        # 多轮廓的清洗返回
        return self if self.is_valid() else Shape.EMPTY

    def __len__(self):
        return len(self.geo.geoms)
