"""
需要三步走：
1. 轮廓自相交规范化（复杂过程，参考 ChatGPT 代码）
2. 内外轮廓相交规范化（可以用 buffer(0)，前提是轮廓自相交已经消除）
3. 多轮廓相交规范化（可以用 unary_union）
"""
import shapely
import jassor.utils as J
from test_coords_func import normalize_single_ring


def main():
    for coords in single_coords:
        lines = normalize_single_ring(coords)
        line = shapely.LinearRing(coords)
        multi_poly = shapely.MultiPolygon(polygons=[shapely.Polygon(shell=ln, holes=[]) for ln in lines])
        print(line.is_valid, [shapely.LinearRing(ln).is_valid for ln in lines], multi_poly.is_valid, multi_poly)
        J.plots([coords, line, *lines, multi_poly])
    # # poly = shapely.Polygon(outer, [inner])
    # poly = shapely.MultiPolygon(polygons=[shapely.Polygon(shell=outer, holes=[]), shapely.Polygon(shell=inner, holes=[])])
    # J.plot(poly)


single_coords = [
    # 典型蝴蝶结自交（八字歧义）✅必自交
    # [(0, 0), (10, 10), (0, 10), (10, 0), (0, 0)],

    # 五角星（Pentagram）✅必自交
    # 取正五边形顶点，按“隔一个连一个”的顺序走：0->2->4->1->3->0
    [(0.00, 10.00), (5.88, -8.09), (-9.51, 3.09), (9.51, 3.09), (-5.88, -8.09), (0.00, 10.00)],

    # # 多次自交的“花瓣环”✅多处交叉（比五角星更容易测试拆分/碎片）
    # # 这是一个手工构造的自交 ring，交叉点>1
    # [(0.0, 10.0), (-3.420201, -9.396926), (6.427876, 7.660444), (-8.660254, -5.0), (9.848078, 1.736482), (-9.848078, 1.736482), (8.660254, -5.0), (-6.427876, 7.660444), (3.420201, -9.396926), (0.0, 10.0)],
    #
    # # 所有点共线（面积=0）✅退化
    # [(0, 0), (5, 0), (10, 0), (0, 0)],
    #
    # # 极瘦近似共线（数值不稳定/可能被认为退化）✅
    # [(0, 0), (1000, 0), (1000, 1e-9), (0, 1e-9), (0, 0)],
    #
    # # 几乎在同一点“交叉”（浮点误差敏感）✅
    # [(0, 0), (10, 10), (0, 10), (10, 0.0000001), (0, 0)],
]

polygon_coords = [
    # 内轮廓越界（outer 已闭合 ✅）
    dict(
        outer=[(1, 1), (10, 1), (10, 10), (1, 10), (1, 1)],
        inners=[[(8, 8), (11, 8), (9, 9), (8, 8)]],
    ),

    # 内轮廓擦边（touch shell，outer 已闭合 ✅）
    dict(
        outer=[(1, 1), (10, 1), (10, 10), (1, 10), (1, 1)],
        inners=[[(8, 8), (10, 8), (9, 9), (8, 8)]],
    ),

    # 内轮廓交叉（outer 原来没闭合，这里修正 ✅）
    dict(
        outer=[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)],
        inners=[
            [(4, 4), (4, 9), (9, 9), (4, 4)],
            [(6, 6), (6, 1), (1, 1), (6, 6)],
        ],
    ),

    # 内轮廓覆盖（outer 原来没闭合，这里修正 ✅）
    dict(
        outer=[(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)],
        inners=[
            [(1, 1), (1, 9), (9, 9), (1, 1)],
            [(4, 4), (4, 6), (6, 6), (4, 4)],
        ],
    ),
]

if __name__ == '__main__':
    main()
