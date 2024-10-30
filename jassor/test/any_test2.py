import shapely
import shapely.affinity as A


def region(l, u, r, d) -> shapely.Polygon:
    return shapely.Polygon([(l, u), (r, u), (r, d), (l, d)], [])


s1 = region(0, 0, 100, 100)
s2 = region(200, 200, 300, 300)
# s2 = A.scale(s1, xfact=1, yfact=2, origin='center')
# s3 = A.rotate(s1, angle=180, origin=(0, 0))

# print(s1)
# print(s2)
# print(s3)

print(s1.intersection(None))
