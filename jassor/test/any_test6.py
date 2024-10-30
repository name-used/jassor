import shapely
from shapely.geometry.polygon import InteriorRingSequence


def region(l, u, r, d) -> shapely.Polygon:
    return shapely.Polygon([(l, u), (r, u), (r, d), (l, d)], [])


s1 = region(0, 0, 100, 100)
s11 = region(10, 10, 20, 20)
s12 = region(30, 30, 40, 40)
s2 = region(200, 200, 300, 300)
s21 = region(210, 210, 220, 220)
s22 = region(230, 230, 240, 240)

ss1 = s1.difference(s11).difference(s12)
ss2 = s2.difference(s21).difference(s22)
ss3 = ss1.union(ss2)

# print(ss3)
# print(s1.exterior)
# tt = ss1.interiors
# tt = [[t.coords, []] for t in tt]
# tt = [shapely.Polygon(shell=t) for t in tt]
tt = shapely.MultiPolygon(polygons=[s1])
print(len(tt.geoms))
# print(tt.area)
# print(tt.is_empty)
print([g for g in tt.geoms])
