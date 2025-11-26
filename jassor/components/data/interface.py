import abc
from typing import Tuple, Union
import numpy as np
from pathlib import Path

num = Union[float, int]


class Reader:
    def __init__(self, path: Union[str, Path], *args, **kwargs):
        self.path = path

    @property
    @abc.abstractmethod
    def level_count(self) -> int:
        raise NotImplemented

    @property
    @abc.abstractmethod
    def base_mpp(self) -> float:
        raise NotImplemented

    def mpp(self, level: int = 0) -> float:
        return self.base_mpp * self.downsample(level)

    @abc.abstractmethod
    def dimension(self, level: int = 0) -> Tuple[int, int]:
        raise NotImplemented

    @abc.abstractmethod
    def downsample(self, level: int = 0) -> float:
        raise NotImplemented

    @abc.abstractmethod
    def region(self, level: int, left: num, up: num, right: num, down: num) -> np.ndarray:
        raise NotImplemented

    def thumb(self, level: int = -1) -> np.ndarray:
        level = level % self.level_count
        w, h = self.dimension(level)
        return self.region(level, 0, 0, w, h)


# class Dataset(torch.utils.data.Dataset, abc.ABC):
#     def __init__(self, source: Any):
#         super().__init__()
#         self.source = source
#         self.samples = []
#
#     def __len__(self):
#         return len(self.samples)
#
#     def __getitem__(self, item):
#         return self.load(self.samples[item])
#
#     def __iter__(self):
#         for i in range(len(self)):
#             yield self[i]
#
#     @abc.abstractmethod
#     def load(self, sample) -> Any: pass
