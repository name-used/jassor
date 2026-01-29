import math
from typing import Iterable, overload, List, Tuple, Union, Optional
import numpy as np
import sys
import shapely
from shapely.ops import unary_union

from .definition import Shape, COORDS, CoordinatesNotLegalException
from .impl_circle import Circle
from .impl_single_simple import SimplePolygon
from .impl_single_complex import ComplexPolygon
from .impl_multi_complex import MultiComplexPolygon
from .normalizer import deintersect


def create_regular_polygon(n: int, len_side: float = None, center_radius: float = None) -> Shape:
    """
    创建正 n 边形，优先使用边长，未提供边长时使用外接圆半径，二者均不提供时，默认生成边长为 1 的正 n 边形
    # 生成的 n 边形总是中心在原点，且一个顶点在 x 轴上
    生成的三角形第一个顶点总是原点，第一条边总是在 x 轴上
    :param n: 边数
    :param len_side: 边长
    :param center_radius: 外接圆半径
    :return: 一个定义为正 n 边形的 Shape
    """
    if len_side:
        # 换算式由 GPT 提供：
        # calc_side_length = 2 * radius * np.sin(np.pi / n)
        # radius = side_length / (2 * np.sin(np.pi / n))
        r = len_side / (2 * math.sin(math.pi / n))
    else:
        r = center_radius or 1
    base_directs = [2 * math.pi / n * i for i in range(n)]
    base_points = [(math.cos(d), math.sin(d)) for d in base_directs]
    outer = [(p * r, q * r) for p, q in base_points]
    # return SimplePolygon(outer=outer)
    shape = SimplePolygon(outer=outer)
    shape -= (r, 0)
    shape.rotate(-90 - 360 / n / 2, origin=(0, 0))
    return shape


def create_triangle(len_sides: Iterable[float], degrees: Iterable[float] = None) -> Shape:
    """
    创建三角形，边长与角度不必全给，只需给够满足确定一个三角形的最小需求即可
    边角序列对应的几何关系是：边1、角1、边2、角2、边3、角3、边1、...
    生成的三角形第一个顶点总是原点，第一条边总是在 x 轴上
    :param len_sides: 边长序列，至少要给一个长度，缺失的边长可以用 None 占位
    :param degrees: 角度序列，若三边长度全给，则可以不提供角度 —— 采用角度制，0 < degree < 180，缺失的角度可以用 None 占位
    :return:
    """
    # 参数标准化
    sides = list(len_sides)
    sides.extend([None] * max(0, 3 - len(sides)))
    dgs = list(degrees or [])
    dgs.extend([None] * max(0, 3 - len(dgs)))
    # 补全三边三角
    sides, dgs = _triangle_complete_arguments(sides, dgs)

    # 几何学角度转化为坐标系倾角
    dgs = [180 - d for d in dgs]
    dgs = [sum(dgs[:i + 1]) for i, _ in enumerate(dgs)]
    assert abs(dgs[-1] - 360) < 0.05, f'角度差过大，请检查输入参数: {len_sides}, {degrees}'

    # 创建三角形
    x1 = y1 = 0
    x2 = sides[0]
    y2 = 0
    # 只有第三个顶点需要计算
    x3 = x2 + math.cos(dgs[0] * math.pi / 180) * sides[1]
    y3 = y2 + math.sin(dgs[0] * math.pi / 180) * sides[1]
    # 但还需要计算第四个顶点，以检查所得形状是否符合要求
    x4 = x3 + math.cos(dgs[1] * math.pi / 180) * sides[2]
    y4 = y3 + math.sin(dgs[1] * math.pi / 180) * sides[2]
    assert abs(x4) + abs(y4) < max(s for s in len_sides if s is not None) * 0.05, f'计算结果不构成三角形，请检查输入参数: {len_sides}, {degrees}'

    return SimplePolygon([(x1, y1), (x2, y2), (x3, y3)])


def _triangle_complete_arguments(sides, dgs):
    if dgs.count(None) <= 1:
        # 有两角，第三角可以直接计算出来
        if dgs.count(None) == 1:
            dgs[dgs.index(None)] = 180 - sum(d for d in dgs if d)
        # 然后用正弦定理补边长
        p = [s is not None for s in sides].index(True)
        for i, s in enumerate(sides):
            if s is not None: continue
            sides[i] = sides[p] / math.sin(dgs[(p + 1) % 3] * math.pi / 180) * math.sin(dgs[(i + 1) % 3] * math.pi / 180)
        return sides, dgs
    # 否则至少有两边
    if sides.count(None) == 1:
        # SSA 不能唯一确定三角形，因此只考虑 SAS，条件不满足直接抛错不管
        assert dgs[(sides.index(None) + 1) % 3] is not None, f'请使用 SSS、AAS、SAS 的方式定义三角形，检查输入参数：{sides}, {dgs}'
        # 正对角有值，用余弦定理补边长
        p = [s is not None for s in sides].index(False)
        sides[p] = (
                           sides[(p + 1) % 3] ** 2 +
                           sides[(p - 1) % 3] ** 2 -
                           2 * sides[(p + 1) % 3] * sides[(p - 1) % 3] * math.cos(
                       dgs[(p + 1) % 3] * math.pi / 180
                   )
                   ) ** 0.5
    # 正弦定理求角度不可靠（钝角锐角问题），因此统一用余弦定理求角度
    for i, d in enumerate(dgs):
        if d is not None: continue
        dgs[i] = math.acos(
            (
                    sides[i] ** 2 +
                    sides[(i + 1) % 3] ** 2 -
                    sides[(i - 1) % 3] ** 2
            ) / (
                    2 * sides[i] * sides[(i + 1) % 3]
            )
        ) * 180 / math.pi
    return sides, dgs


def create_polygon(len_sides: Iterable[float], degrees: Iterable[float], ring_close: bool = True) -> Shape:
    """
    由于任意多边形不能简单由边长信息确定，所以必须给全边长和角度的参数
    :param len_sides:   边长数组
    :param degrees:     角度数组
    :param ring_close:  描述所给轮廓是否包含最后一条边和最后一个角
                    默认为真，为真时，依路径得到的最后一个点应当和起始点重合
                    为假时，依路径得到的最后一个点应当与起点不重合
    :return:
    """
    # 几何学角度转化为坐标系倾角
    dgs = [180 - d for d in degrees]
    dgs = [sum(dgs[:i + 1]) for i, _ in enumerate(dgs)]
    if ring_close:
        assert abs(dgs[-1] - 360) < 5, f'角度差过大，请检查输入参数: {len_sides}, {degrees}'
    dgs.insert(0, 0)

    points = [(0, 0)]
    for s, d in zip(len_sides, dgs):
        x0, y0 = points[-1]
        x = x0 + math.cos(d * math.pi / 180) * s
        y = y0 + math.sin(d * math.pi / 180) * s
        points.append((x, y))

    if ring_close:
        assert abs(max(points[-1])) < max(len_sides) * 0.05, f'计算结果不符合预期，请检查输入参数: {len_sides}, {degrees}'
        return SimplePolygon(points[:-1])
    else:
        return SimplePolygon(points)


def create_sector(radius: float, degree: float, num: int = 100) -> Shape:
    """
    创建一个扇形
    :param radius:  扇形所对应圆的半径
    :param degree:  扇形所对应圆心角
    :param num:     描述扇形所用轮廓点数
    :return:
    """
    # 入参矫正检查
    if abs(degree) < 0.05: return Shape.EMPTY
    if abs(degree) >= 360: return Circle(0, 0, radius, num)
    # 角度值换弧度制
    angle = degree * math.pi / 180
    base_directs = [angle / num * i for i in range(num + 1)]
    base_points = [(math.cos(d), math.sin(d)) for d in base_directs]
    outer = [(0., 0.)] + [(p * radius, q * radius) for p, q in base_points]
    return SimplePolygon(outer=outer)


def create_from_adjacencies(outers: List[COORDS], inners: List[COORDS], adjacencies: List[int]):
    inners = inners or []
    adjacencies = adjacencies or []
    poly_coords = [(outer, []) for outer in outers]
    for inner, adjacency in zip(inners, adjacencies):
        if not (0 <= adjacency < len(poly_coords)): continue
        poly_coords[adjacency][1].append(inner)
    return create_from_poly_coords(poly_coords)


def create_from_hierarchy(contours: List[COORDS], hierarchy: Optional[np.ndarray]):
    if hierarchy is None:  # hierarchy[0] = [(next, prev, child, parent)]
        return Shape.EMPTY
    # cv2 愚蠢的设计，contours 是 [n, 1, 2], hirarchy 是 [1, n, 4]
    hierarchy = hierarchy if len(hierarchy.shape) == 2 else hierarchy[0]
    poly_coords = []
    for i, (contour, h) in enumerate(zip(contours, hierarchy)):
        if h[-1] == -1:
            if isinstance(contour, np.ndarray):
                contour = contour.tolist() if len(contour.shape) == 2 else contour[:, 0, :].tolist()
            poly_coords.append((contour, []))
        else:
            poly_coords.append(None)
    for i, (contour, h) in enumerate(zip(contours, hierarchy)):
        if h[-1] != -1:
            if isinstance(contour, np.ndarray):
                contour = contour.tolist() if len(contour.shape) == 2 else contour[:, 0, :].tolist()
            poly_coords[h[-1]][1].append(contour)
    poly_coords = [x for x in poly_coords if x is not None]
    return create_from_poly_coords(poly_coords)


def create_from_poly_coords(poly_coords: Union[List[List[COORDS]], List[Tuple[COORDS, List[COORDS]]]]):
    legal_coords_list = []
    for poly in poly_coords:
        if isinstance(poly, list):
            outer, *inners = poly
        else:
            outer, inners = poly

        outers = deintersect(outer)
        inners = sum([deintersect(inner) for inner in inners], [])
        if len(outers) == 0:
            # 通常是因为轮廓点数不达标，在这种状态下可以直接丢弃
            continue
        if len(outers) > 1:
            # 单一轮廓修复后变成多个轮廓，说明轮廓存在自相交问题，此时需拆分外轮廓，并按配位关系重组内轮廓
            sys.stderr.write(f'creating multi polygon found self-intersect coord=={outer}\n')
            polygons = [shapely.Polygon(shell=outer, holes=[]) for outer in outers]
            coords = [(polygon.exterior.coords, [inner for inner in inners if not polygon.disjoint(shapely.LineString(inner))]) for polygon in polygons]
        else:
            polygon = shapely.Polygon(shell=outers[0], holes=[])
            coords = [(polygon.exterior.coords, [inner for inner in inners if not polygon.disjoint(shapely.LineString(inner))])]
        legal_coords_list.extend(coords)

    # 对用户输入进行检查和修复
    geo = shapely.MultiPolygon(polygons=legal_coords_list)
    try:
        geo = unary_union(geo)
    except Exception as e:
        sys.stderr.write(f'geometry invalid caused by {e}\n')
    geo = geo.buffer(0)

    if geo.is_empty:
        # geo 是空，这种没办法，只能报错处理
        return Shape.EMPTY
    elif isinstance(geo, shapely.Polygon):
        # 如果 geo 是单个图形，就返回 ComplexPolygon
        return ComplexPolygon(geo=geo)
    elif isinstance(geo, shapely.MultiPolygon):
        # 如果 geo 是多个图形，就返回 MultiComplexPolygon
        return MultiComplexPolygon(geo=geo)
    else:
        # 我暂时想不到什么情况可能会在 buffer(0) 的条件下出现 poly、multi_poly 以外的数据类型，等出现报错再说吧。。
        raise AssertionError(f'Unexpected geometry type after buffer(0): {type(geo)}')
