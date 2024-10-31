import shapely
from shapely.ops import unary_union


def region(l, u, r, d) -> shapely.Polygon:
    return shapely.Polygon([(l, u), (r, u), (r, d), (l, d)], [])


s1 = region(0, 0, 100, 100)
s2 = region(50, 50, 250, 250)
s3 = region(200, 200, 300, 300)

s4 = region(150, 150, 200, 200)

ss = shapely.MultiPolygon(polygons=[s1, s2, s3])

print(ss)
print(ss.is_empty)
print(ss.is_valid)
print(ss.is_simple)
print(ss.is_ring)
print(unary_union(ss))
print(unary_union(ss).is_simple)
print(unary_union(ss).is_valid)
print(unary_union(ss).difference(s4))
print(unary_union(ss).difference(s4).is_simple)
