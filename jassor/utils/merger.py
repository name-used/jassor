from typing import Union, Tuple
import numpy as np


class Merger(object):
    def __init__(
            self,
            temp: Union[np.ndarray, Tuple[int, ...]],
            kernel: Union[np.ndarray, Tuple[int, ...]],
            dtype: type = np.float32,
            steep: float = 4,
            eps: float = 1e-17,
    ):
        """
        一个相对通用的融合器，参数可以直接提供一个 ndarray，也可以提供一个用于生成 ndarray 的形状
        :param temp: 融合模板，用来缓存融合结果
        :param kernel: 融合系数，用来实现有差融合，需要广播的维度请设为 1
        :param dtype: 以参数方式生成 ndarray 时的数据类型
        :param steep: 以参数方式生成 kernel 时，kernel 形状的描述符，kernel 越大，中心区域价值占比越高
        """
        if isinstance(temp, tuple):
            temp = np.zeros(shape=temp, dtype=dtype)
        if isinstance(kernel, tuple):
            kernel = self.get_kernel(shape=kernel, steep=steep).astype(dtype)
        assert len(temp.shape) == len(kernel.shape), 'attention : temp.shape.length eq kernel.shape.length eq patch.shape.length'
        self._temp = temp
        self._kernel = kernel
        # kernel 中维度数为 1 视为需要广播，helper 中置为 1 即可
        # 否则视为需要贴片，按照 temp 的维度数来设置
        helper_shape = tuple(1 if k==1 else t for k, t in zip(kernel.shape, temp.shape))
        self._helper = np.zeros(shape=helper_shape, dtype=dtype) + eps

    @staticmethod
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

    def set(self, patch: np.ndarray, grid: Tuple[Union[int, None], ...]) -> None:
        """
        贴图方法，patch 表示待贴图块，grid 表示图块坐标
        :param patch: 需确保 dtype 与 kernel 一致，shape 与 kernel 在广播形式下一致
        :param grid: 整数坐标，无需计算（需要广播的维度，或锁定满填充的维度）的维度置为 None
        """
        # 计算图
        patch = patch * self._kernel
        # 将 grid 坐标 limit 在坐标范围之内，构成贴片
        # 针对 temp 的计算
        temp_grid = tuple(
            slice(None) if g is None else slice(max(0, g), min(s, max(0, g + k)))
            for s, k, g in zip(self._temp.shape, self._kernel.shape, grid)
        )
        # # 针对 helper 的计算
        # help_grid = tuple(
        #     (0, 1) if g is None else (max(0, g), min(s, g + k))
        #     for s, k, g in zip(self._temp.shape, patch.shape, grid)
        # )
        # 针对 patch 的计算
        patch_grid = tuple(
            slice(None) if g is None else slice(max(0, -g), min(k, max(0, s - g)))
            for s, k, g in zip(self._temp.shape, self._kernel.shape, grid)
        )
        # # 针对 kernel 的计算
        # kernel_grid = tuple(
        #     (0, 1) if g is None else (max(0, -g), min(k, s - g))
        #     for s, k, g in zip(self._temp.shape, patch.shape, grid)
        # )
        # 以上面的计算为基础执行贴图方法
        self._temp[temp_grid] += patch[patch_grid]
        self._helper[temp_grid] += self._kernel[patch_grid]

        # for (x, y), target in zip(grids, targets.cpu()):
        #     temp_left = max(0, x)
        #     temp_up = max(0, y)
        #     temp_right = min(self.w, x + self.ksize)
        #     temp_down = min(self.h, y + self.ksize)
        #     patch_left = max(0, -x)
        #     patch_up = max(0, -y)
        #     patch_right = min(self.ksize, self.w - x)
        #     patch_down = min(self.ksize, self.h - y)
        #     # print(x, y, target[patch_up: patch_down, patch_left: patch_right, :].shape, self.target[temp_up: temp_down, temp_left: temp_right, :].shape)
        #     self.target[temp_up: temp_down, temp_left: temp_right, :] += target[patch_up: patch_down, patch_left: patch_right, :]
        #     self._helper[temp_up: temp_down, temp_left: temp_right, :] += self.k[patch_up: patch_down, patch_left: patch_right, :]

    def tail(self) -> np.ndarray:
        return self._temp / self._helper
