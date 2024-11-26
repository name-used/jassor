import numpy as np
import matplotlib.pyplot as plt

# 示例复数数组
complex_array = np.array([1 + 1j, -1 + 1j, -1 - 1j, 1 - 1j, 2 + 2j, 3 - 1j])

# 计算辐角（弧度）
angles = np.angle(complex_array)

# 提取实部和虚部
real_parts = complex_array.real
imag_parts = complex_array.imag

# 创建图形
plt.figure(figsize=(8, 8))
ax = plt.gca()

# 绘制复数矢量
for real, imag, angle in zip(real_parts, imag_parts, angles):
    plt.quiver(0, 0, real, imag, angles='xy', scale_units='xy', scale=1, color=plt.cm.hsv((angle + np.pi) / (2 * np.pi)))
    plt.text(real, imag, f"{np.degrees(angle):.1f}°", fontsize=10, ha='center', va='center')

# 坐标轴设置
ax.axhline(0, color='gray', linestyle='--', linewidth=0.5)
ax.axvline(0, color='gray', linestyle='--', linewidth=0.5)
plt.grid(alpha=0.3)

# 设置图形范围
max_val = np.max(np.abs(complex_array)) * 1.2
plt.xlim(-max_val, max_val)
plt.ylim(-max_val, max_val)

# 添加标题
plt.title("复数及其辐角可视化", fontsize=14)
plt.xlabel("实部", fontsize=12)
plt.ylabel("虚部", fontsize=12)

# 等比例显示
plt.gca().set_aspect('equal', adjustable='box')

# 显示颜色映射
sm = plt.cm.ScalarMappable(cmap='hsv', norm=plt.Normalize(vmin=-np.pi, vmax=np.pi))
# sm.set_array([])
# plt.colorbar(sm, ticks=[-np.pi, -np.pi/2, 0, np.pi/2, np.pi], label="ag")

# 显示图形
plt.show()
