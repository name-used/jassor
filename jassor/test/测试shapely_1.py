import shapely
import shapely.affinity as A

import jassor.utils as J
import jassor.shape as S


def main():
    # J.plot(S.Region(0, 0, 1, 1) ** 15)
    mytest_creator()


def mytest_creator():
    # s1 = S.create_polygon(len_sides=[], degrees=[])
    s1 = S.create_regular_polygon(8, len_side=1)
    J.plot(s1)


def mytest_jshape():
    s1 = S.Region(0, 0, 100, 100)
    s2 = S.Region(10, 10, 20, 20)
    s3 = S.Circle(50, 50, 20)

    s4 = s1 >> s2 >> s3
    J.plot(s1)
    J.plot(s2)
    J.plot(s3)
    J.plot(s4)
    J.plots([s1 | s2 * 5 + (200, 0) | s4 + (200, 200)])
    J.plots([s1, s2, s3, None, S.EMPTY, S.FULL, shapely.Point(), shapely.LineString(), shapely.Polygon()])


def mytest_shapely():
    s1 = shapely.Point((1, 1))
    s2 = shapely.LineString([(2, 2), (2, 3), (3, 3), (3, 4)])
    s3 = shapely.LinearRing([(12, 12), (12, 13), (13, 13)])
    s4 = shapely.Polygon([(100, 100), (200, 100), (200, 200), (100, 200)], [
        [(110, 110), (120, 110), (120, 120), (110, 120)],
        [(150, 150), (160, 150), (160, 160), (150, 160)],
    ])
    s5 = shapely.MultiPoint(points=[(1, 1), (2, 2), (3, 3)])
    s6 = shapely.MultiLineString(lines=[s2, s3])
    s7 = shapely.MultiPolygon(polygons=[s4, A.translate(s4, 120, 120)])
    s8 = shapely.GeometryCollection(geoms=[s1, s2, s3, s4])

    J.plots([s1, s2, s3, s4, s5, s6, s7, s8, None])


main()
