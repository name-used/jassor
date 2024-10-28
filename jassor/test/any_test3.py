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

# print(s1)
# print(s1.exterior)
# print(shapely.Polygon(shell=s1.exterior))
# print(s1.interiors)
# print(InteriorRingSequence(s1))

ss1 = s1.difference(s11).difference(s12)
# ss2 = s11.union(s12)
# ss3 = s1.difference(s11).difference(s12).union(s2.difference(s21).difference(s22))

# print(list(s1.exterior.coords))
# print(list(list(i.coords) for i in s1.interiors))
#
# print(list(ss1.exterior.coords))
# print(list(list(i.coords) for i in ss1.interiors))
#
# print(list(list(s.exterior.coords) for s in ss2.geoms))
# print(list(list(list(i.coords) for i in s.interiors) for s in ss2.geoms))
#
# print(list(list(s.exterior.coords) for s in ss3.geoms))
# print(list(list(list(i.coords) for i in s.interiors) for s in ss3.geoms))

inners = InteriorRingSequence(ss1)
tt = shapely.MultiPolygon(polygons=inners)
print(tt)
print(type(tt))
# print(tt.geoms)
# print(tt.boundary)
# print(tt.is_empty)
# tt = shapely.MultiPolygon(polygons=InteriorRingSequence(ss1))
# print(list(list(s.exterior.coords) for s in tt.geoms))
# print(list(list(list(i.coords) for i in s.interiors) for s in shapely.MultiPolygon(polygons=InteriorRingSequence(ss1)).geoms))
