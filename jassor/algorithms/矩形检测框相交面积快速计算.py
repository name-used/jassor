import numpy as np


def main():
    # 使用自定义矩阵乘法
    p1 = p2 = np.asarray([
        [10, 10, 5, 5],
        [10, 8, 5, 5],
        [10, 15, 6, 6],
        [10, 20, 7, 7]
    ], dtype=np.float32)
    inters = rects_inter_area(p1, p2)
    print("使用 Numba 的自定义矩阵乘法结果：\n", inters)


def rects_inter_area(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:

    assert p1.shape[1] == p2.shape[1] == 4, "要求点列使用 (x, y, w, h) 格式"

    # 创建结果矩阵
    inters = np.zeros((p1.shape[0], p2.shape[0]), dtype=np.float32)

    # 自定义矩阵乘法逻辑
    # min(max(0, (wi+wj)/2-abs(xi-xj)), wi, wj) * min(max(0, (hi+hj)/2-abs(yi-yj)), hi, hj)
    for i in range(p1.shape[0]):
        w = (p1[i, 2] + p2[:, 2]) / 2 - abs(p1[i, 0] - p2[:, 0])
        h = (p1[i, 3] + p2[:, 3]) / 2 - abs(p1[i, 1] - p2[:, 1])
        w = np.stack([
            np.zeros(len(p2)) + p1[i, 2],
            p2[:, 2],
            np.clip(w, 0, None)
        ])
        h = np.stack([
            np.zeros(len(p2)) + p1[i, 3],
            p2[:, 3],
            np.clip(h, 0, None)
        ])
        inters[i, :] = w.min(axis=0) * h.min(axis=0)

    return inters


main()
