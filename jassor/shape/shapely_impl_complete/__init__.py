from .definition import Shape, Single as SingleShape, Multi as MultiShape
from .impl_multi_simple import MultiSimplePolygon
from .impl_multi_complex import MultiComplexPolygon
from .impl_region import Region
from .impl_circle import Circle
from .impl_single_simple import SimplePolygon
from .impl_single_complex import ComplexPolygon
from .impl_empty import Empty
from .impl_full import Full
from .polygon_creators import create_polygon, create_triangle, create_regular_polygon


EMPTY = Shape.EMPTY
FULL = Shape.FULL

__all__ = [
    'Shape',
    'SingleShape',
    'Region',
    'Circle',
    'SimplePolygon',
    'ComplexPolygon',
    'MultiShape',
    'MultiSimplePolygon',
    'MultiComplexPolygon',
    'EMPTY',
    'FULL',
    'create_polygon',
    'create_triangle',
    'create_regular_polygon',
]

'''
关于 shapely 中的类型:
'Point',
'LineString',
'LinearRing',
'Polygon',
'MultiPoint',
'MultiLineString',
'MultiPolygon',
'GeometryCollection',
'''
