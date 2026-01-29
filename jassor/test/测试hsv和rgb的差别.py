import numpy as np
import jassor.utils as J
from PIL import Image


# def main():
#     x = J.random_rainbow_curves((500, 500, 3), s=101)
#     img1 = Image.fromarray(x, mode='RGB')
#     img2 = img1.convert('HSV')
#     y = np.asarray(img2)
#     print(y.max(axis=(0, 1)))
#     J.plots([x, y])

def main():
    x = np.zeros((500, 500, 3), dtype=np.uint8) + 254
    xs = [Image.fromarray((x - [k*50, j*60, i*80]).astype(np.uint8), mode='HSV') for i in range(3) for j in range(4) for k in range(5)]
    J.plots(xs, ticks=False)


main()


# def rgb_image_to_hsv(rgb: np.ndarray) -> np.ndarray:
#     """
#     rgb: (..., 3)
#       - uint8: 按 0-255 处理
#       - float: 假定已经是 0-1
#
#     返回 hsv: (..., 3)，float32，h,s,v 都在 [0,1]，h*360 是角度
#     """
#     rgb = rgb.astype(np.float32)
#     if rgb.dtype != np.float32 and rgb.max() > 1.0:
#         rgb = rgb / 255.0
#     else:
#         # 如果本来就是 float32 但范围是 0-255，可以自己加一行 rgb /= 255
#         pass
#
#     r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
#
#     cmax = np.max(rgb, axis=-1)
#     cmin = np.min(rgb, axis=-1)
#     delta = cmax - cmin
#
#     # v
#     v = cmax
#
#     # s
#     s = np.zeros_like(v)
#     mask = cmax > 0
#     s[mask] = delta[mask] / cmax[mask]
#
#     # h
#     h = np.zeros_like(v)
#
#     # 避免除零
#     nonzero = delta > 0
#     r_eq = (cmax == r) & nonzero
#     g_eq = (cmax == g) & nonzero
#     b_eq = (cmax == b) & nonzero
#
#     h[r_eq] = ((g[r_eq] - b[r_eq]) / delta[r_eq]) % 6
#     h[g_eq] = (b[g_eq] - r[g_eq]) / delta[g_eq] + 2
#     h[b_eq] = (r[b_eq] - g[b_eq]) / delta[b_eq] + 4
#
#     h = (h / 6.0)  # [0,1)
#
#     hsv = np.stack([h, s, v], axis=-1)
#     return hsv
#
#
# def hsv_image_to_rgb(hsv: np.ndarray) -> np.ndarray:
#     """
#     hsv: (..., 3)，h,s,v 都在 [0,1]
#     返回 rgb: (..., 3)，float32，范围 [0,1]
#     需要 0-255 的话最后自己乘 255、astype(uint8)
#     """
#     h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
#
#     rgb = np.zeros_like(hsv, dtype=np.float32)
#     r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
#
#     # 灰度区域
#     gray = s == 0
#     r[gray] = v[gray]
#     g[gray] = v[gray]
#     b[gray] = v[gray]
#
#     # 彩色区域
#     not_gray = ~gray
#     h_ng = h[not_gray] * 6.0
#     i = np.floor(h_ng).astype(int)
#     f = h_ng - i
#
#     p = v[not_gray] * (1.0 - s[not_gray])
#     q = v[not_gray] * (1.0 - s[not_gray] * f)
#     t = v[not_gray] * (1.0 - s[not_gray] * (1.0 - f))
#
#     i_mod = i % 6
#
#     idx0 = i_mod == 0
#     idx1 = i_mod == 1
#     idx2 = i_mod == 2
#     idx3 = i_mod == 3
#     idx4 = i_mod == 4
#     idx5 = i_mod == 5
#
#     # 建一个视图方便赋值
#     r_ng, g_ng, b_ng = r[not_gray], g[not_gray], b[not_gray]
#
#     r_ng[idx0], g_ng[idx0], b_ng[idx0] = v[not_gray][idx0], t[idx0], p[idx0]
#     r_ng[idx1], g_ng[idx1], b_ng[idx1] = q[idx1], v[not_gray][idx1], p[idx1]
#     r_ng[idx2], g_ng[idx2], b_ng[idx2] = p[idx2], v[not_gray][idx2], t[idx2]
#     r_ng[idx3], g_ng[idx3], b_ng[idx3] = p[idx3], q[idx3], v[not_gray][idx3]
#     r_ng[idx4], g_ng[idx4], b_ng[idx4] = t[idx4], p[idx4], v[not_gray][idx4]
#     r_ng[idx5], g_ng[idx5], b_ng[idx5] = v[not_gray][idx5], p[idx5], q[idx5]
#
#     return rgb
