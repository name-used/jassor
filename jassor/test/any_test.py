from typing import Union, Tuple
import numpy as np


def get_kernel(shape: Tuple[int, ...], steep: float) -> np.ndarray:
    # 第一步：获得一个对称区间，x = np.arange(w).astype(np.float32) - (w - 1)/2
    # 第二步：计算高斯函数，x = exp(-1/2 (x/sigma) ** 2)，其中 sigma = size / steep
    # 第三步：乘到 kernel 里
    kernel = np.asarray([1], dtype=np.float32)
    for i, size in enumerate(shape):
        sigma = size / steep
        x = np.arange(size).astype(np.float32) - (size - 1) / 2
        x = np.exp(-1 / 2 * (x / sigma) ** 2)
        x /= x.mean()
        kernel = kernel[..., None] @ x[(None,) * (i + 1)]
    return np.ascontiguousarray(kernel[0])


kernel = get_kernel((512, 512), 4)

print(kernel.shape)
print(kernel.max())
print(kernel.min())
print(kernel.sum())
print(kernel.mean())
print(kernel)

