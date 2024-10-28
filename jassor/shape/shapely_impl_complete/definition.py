import abc
import io
import json
import pickle
from io import BufferedIOBase

from shapely.geometry.base import BaseGeometry

from ..interface import Shape as Interface


class Shape(Interface, abc.ABC):
    """
    平面图形计算库的 shapely - impl，接口定义参考 Interface，类型结构如下所示：

    Shape:      一切类型的超类，标识符代称
        EMPTY:      唯一实例，代表空集，表示平面上没有任何元素在 Shape 中
        FULL:       唯一实例，代表全集，表示全平面都在 Shape 中
        Single:         若 Shape 中的全部元素相互联通，称之为”单一图形“，对应”多组图形“ —— 但 EMPTY 和 FULL 不属于 Single
            Region:                 矩形
            Circle：                 圆形
            SimplePolygon:          简单多边形，”简单“在这里指的是”单连通“，对应”复连通“
            ComplexPolygon:         复杂多边形，”复杂“在这里指的是”复连通“，对应”单连通“
        Multi:         若 Shape 中的至少存在两个元素相互不能联通，称之为”多组图形“，对应”单一图形“ —— 但 EMPTY 和 FULL 不属于 Multi
            MultiSimplePolygon:      多组简单多边形
            MultiComplexPolygon:     多组复杂多边形

    基于本人需求考虑，全部图形均用轮廓数组表示，包括圆，也直接写作一族点列，后续不再区分”图形“与”轮廓“的概念
    """
    EMPTY = None
    FULL = None

    __slots__ = ('_geo', '_reversed')

    def __bool__(self) -> bool:
        return self != self.EMPTY and self != self.FULL

    @property
    def geo(self) -> BaseGeometry:
        return self._geo

    def reversed(self) -> bool:
        return self._reversed

    def is_valid(self) -> bool:
        geo = self.geo
        return geo is not None and geo.is_valid and not geo.is_empty and geo.area > 0

    def is_joint(self, other) -> bool:
        if self.is_valid() and other.is_valid():
            return not self.geo.disjoint(other.geo)
        else:
            return False

    # @abc.abstractmethod
    # def clean(self):
    #     raise NotImplementedError

    def loads(self, lines: str):
        tp = lines[0].upper()
        if tp == 'EMPTY':
            return Shape.EMPTY
        if tp == 'FULL':
            return Shape.FULL
        tp = Shape.map_cls(tp)
        rvs = bool(lines[1])
        points = json.loads(lines[2])
        return tp(from_p=points, reverse=rvs)

    def loadb(self, f: io.BufferedReader):
        tp, rvs, points = pickle.load(f)
        if tp == 'EMPTY':
            return Shape.EMPTY
        if tp == 'FULL':
            return Shape.FULL
        tp = Shape.map_cls(tp)
        return tp(from_p=points, reverse=rvs)

    @staticmethod
    def map_cls(tp: str) -> type:
        return {
            'REGION': Single.REGION,
            'CIRCLE': Single.CIRCLE,
            'SIMPLEPOLYGON': Single.SIMPLE,
            'COMPLEXPOLYGON': Single.COMPLEX,
            'MULTISIMPLEPOLYGON': Multi.SIMPLE,
            'MULTICOMPLEXPOLYGON': Multi.COMPLEX,
        }[tp]


class Single(Shape, abc.ABC):
    # 单形,复形的定义
    REGION = None
    SIMPLE = None
    COMPLEX = None

    __slots__ = ()

    @staticmethod
    def asSimple(shape: Shape):
        if not shape: return Shape.EMPTY
        assert isinstance(shape, Single), 'Multi 类型无法转换为 Single'
        return shape.outer

    @staticmethod
    def asComplex(shape: Shape):
        if not shape: return Shape.EMPTY
        assert isinstance(shape, Single), 'Multi 类型无法转换为 Single'
        return Single.COMPLEX(single=shape)


class Multi(Shape, abc.ABC):
    # 多凸形,多单形,多复形的定义
    CONVEX = None
    SIMPLE = None
    COMPLEX = None

    __slots__ = ()

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

    def __len__(self):
        return len(self.geo.geoms)
