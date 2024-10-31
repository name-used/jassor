import shapely


s1 = shapely.Polygon([(0, 0), (0, 10), (20, 10), (20, 20), (10, 20),  (10, 0),  (0, 0)], [])
ss1 = shapely.MultiPolygon(polygons=[s1])
l1 = shapely.Point((0, 1))
c1 = shapely.GeometryCollection([s1, ss1, l1])

print(isinstance(s1, shapely.Polygon))
print(isinstance(s1, shapely.MultiPolygon))
print(isinstance(s1, shapely.Point))
print(isinstance(s1, shapely.LineString))
print(isinstance(s1, shapely.LinearRing))
print(isinstance(s1, shapely.MultiPoint))
print(isinstance(s1, shapely.MultiLineString))
print(isinstance(s1, shapely.GeometryCollection))

print('============================')

print(isinstance(ss1, shapely.Polygon))
print(isinstance(ss1, shapely.MultiPolygon))
print(isinstance(ss1, shapely.Point))
print(isinstance(ss1, shapely.LineString))
print(isinstance(ss1, shapely.LinearRing))
print(isinstance(ss1, shapely.MultiPoint))
print(isinstance(ss1, shapely.MultiLineString))
print(isinstance(ss1, shapely.GeometryCollection))

print('============================')

print(isinstance(c1, shapely.Polygon))
print(isinstance(c1, shapely.MultiPolygon))
print(isinstance(c1, shapely.Point))
print(isinstance(c1, shapely.LineString))
print(isinstance(c1, shapely.LinearRing))
print(isinstance(c1, shapely.MultiPoint))
print(isinstance(c1, shapely.MultiLineString))
print(isinstance(c1, shapely.GeometryCollection))


"""
'Point',
'LineString',
'LinearRing',
'Polygon',
'MultiPoint',
'MultiLineString',
'MultiPolygon',
'GeometryCollection',
"""
