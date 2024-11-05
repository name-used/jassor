import matplotlib.pyplot as plt
from shapely.geometry import Polygon

# 创建一个含孔洞的多边形
outer_ring = [(1, 1), (4, 1), (4, 4), (1, 4)]
hole = [(2, 2), (2, 3), (3, 3), (3, 2)]

# 创建 Shapely Polygon
polygon_with_hole = Polygon(outer_ring, [hole])

# 获取外环和孔洞的坐标
x_outer, y_outer = polygon_with_hole.exterior.xy
x_hole, y_hole = polygon_with_hole.interiors[0].xy

# 创建图形和坐标轴
fig, ax = plt.subplots()

# 绘制外环
ax.fill(x_outer, y_outer, color='blue', alpha=0.5, label='Outer Polygon')

# 绘制孔洞
ax.fill(x_hole, y_hole, color='white', alpha=1, label='Hole')

# 设置坐标轴
ax.set_xlim(0, 5)
ax.set_ylim(0, 5)
ax.set_aspect('equal')
ax.set_title('Polygon with Hole')
ax.legend()

# 显示图形
plt.show()
