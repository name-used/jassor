import shapely
from shapely.ops import unary_union


def region(l, u, r, d) -> shapely.Polygon:
    return shapely.Polygon([(l, u), (r, u), (r, d), (l, d)], [])


s1 = region(0, 0, 100, 100)
s2 = region(20, 20, 40, 40)

# ss = s1.difference(s2)
ss = shapely.MultiPolygon(polygons=[s1])

print(ss)
print(ss.is_empty)
print(ss.is_valid)
print(ss.is_simple)
print(ss.is_ring)

# print(bool(s1.interiors))
# print(bool(ss.interiors))

print(ss.buffer(0))
