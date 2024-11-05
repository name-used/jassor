from __future__ import annotations
import abc
import shapely
from shapely.geometry.base import BaseGeometry
from ..interface import ShapeInterface

MIN_AREA = 1e-7


class Shape(ShapeInterface['Shape'], abc.ABC):
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
        return self.geo is not None and not self.geo.is_empty

    def __str__(self) -> str:
        tp = type(self).__name__
        rvs = "neg" if self.reversed else "pos"
        xy = tuple(round(p, 1) for p in self.center)
        area = round(self.area, 2)
        bounds = tuple(round(p, 1) for p in self.bounds)
        return f'JassorShape:{tp} {rvs} at {xy} with area {area} in region {bounds}'

    @property
    def geo(self) -> BaseGeometry:
        return self._geo

    @property
    def reversed(self) -> bool:
        return self._reversed

    def is_valid(self) -> bool:
        geo = self.geo
        return geo is not None and geo.is_valid and not geo.is_empty and geo.area > 0

    # @abc.abstractmethod
    # def clean(self):
    #     raise NotImplementedError

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
    CIRCLE = None
    SIMPLE = None
    COMPLEX = None

    __slots__ = ()

    @staticmethod
    def asSimple(shape: Shape) -> Single:
        shape = Single.asComplex(shape)
        return Single.SIMPLE(single=shape.outer, reverse=shape.reversed)

    @staticmethod
    def asComplex(shape: Shape) -> Single:
        if not shape:
            return Single.COMPLEX(reverse=shape.reversed)
        if isinstance(shape, Single):
            geo = shape.geo
        else:
            # 多轮廓是可以兼容单轮廓的，所以也应该提供相应的向回转换方法
            geo = shape.geo
            assert isinstance(geo, shapely.MultiPolygon), f'geo 类型有问题: {geo}'
            if len(geo.geoms) == 0:
                # 没有轮廓就直接给个空的就行
                geo = shapely.Polygon()
            elif len(geo.geoms) == 1:
                # 只有一个轮廓那最好
                geo = geo.geoms[0]
            elif ConvertMulti2SingleException.mode == 'ignore':
                # 忽略模式
                geos = list(geo.geoms)
                geos.sort(key=lambda g: g.area, reverse=True)
                geo = geos[0]
            elif ConvertMulti2SingleException.mode == 'smart':
                # 智慧模式
                geos = list(geo.geoms)
                geos.sort(key=lambda g: g.area, reverse=True)
                if abs(1 - geos[0].area / geo.area) < ConvertMulti2SingleException.thresh:
                    geo = geos[0]
                else:
                    raise ConvertMulti2SingleException(f'Multi 轮廓长度为 {len(geo.geoms)}，'
                                                       f'其中最大的单一轮廓面积是 {geos[0].area}，总面积是 {geo.area}，'
                                                       f'占比为 {geos[0].area / geo.area} 低于{1 - ConvertMulti2SingleException.thresh}，'
                                                       f'不能转换')
            else:
                # 报错模式
                raise ConvertMulti2SingleException(f'Multi 轮廓长度为 {len(geo.geoms)}，不能转换')
        return Single.COMPLEX(geo=geo, reverse=shape.reversed)


class Multi(Shape, abc.ABC):
    # 多凸形,多单形,多复形的定义
    CONVEX = None
    SIMPLE = None
    COMPLEX = None

    __slots__ = ()

    @staticmethod
    def asSimple(shape: Shape) -> Multi:
        shape = Multi.asComplex(shape)
        return Multi.SIMPLE(geo=shape.outer.geo, reverse=shape.reversed)

    @staticmethod
    def asComplex(shape: Shape) -> Multi:
        if not shape:
            return Multi.COMPLEX(reverse=shape.reversed)
        if isinstance(shape, Multi):
            geo = shape.geo
        else:
            # 多轮廓可以兼容单轮廓，但必须要改类型，因为只有多轮廓里才有 .geoms 属性
            geo = shapely.MultiPolygon(polygons=[shape.geo])
        return Multi.COMPLEX(geo=geo, reverse=shape.reversed)

    def __len__(self) -> int:
        return len(self.geo.geoms)


class ConvertMulti2SingleException(Exception):
    mode = 'error'
    thresh = 0.05
    """
    当此处 mode 设置为 error 时，一个 MultiShape 转化为 SingleShape 会报错
    当此处 mode 设置为 ignore 时，一个 MultiShape 转化为 SingleShape 时会直接选择面积最大的作为结果
    当此处 mode 设置为 smart 时，会根据最大面积占总面积比例决定报错还是忽略
    """

    @staticmethod
    def mode_error():
        ConvertMulti2SingleException.mode = 'error'

    @staticmethod
    def mode_ignore():
        ConvertMulti2SingleException.mode = 'ignore'

    @staticmethod
    def mode_smart(thresh: float = 0.05):
        ConvertMulti2SingleException.mode = 'smart'
        ConvertMulti2SingleException.thresh = thresh


class CoordinatesNotLegalException(Exception):
    pass


class NoParametersException(Exception):
    pass
