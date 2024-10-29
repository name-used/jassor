import shapely
from shapely.geometry.polygon import InteriorRingSequence


def region(l, u, r, d) -> shapely.Polygon:
    return shapely.Polygon([(l, u), (r, u), (r, d), (l, d)], [])


# s1 = region(0, 0, 100, 100)
s11 = region(10, 10, 20, 20)
s12 = region(30, 30, 40, 40)
# s2 = region(200, 200, 300, 300)
s21 = region(210, 210, 220, 220)
s22 = region(230, 230, 240, 240)

# ss1 = s11.union(s12)
ss2 = s21.union(s22)

# tt = shapely.MultiPolygon(polygons=[s11, s12, *ss2.geoms])
tt = shapely.MultiPolygon(polygons=[])
print(tt)
print(list(tt.geoms))
