import abc
from typing import Tuple, Union, Literal, overload
import numpy as np
from PIL.Image import Image
from pathlib import Path

num = Union[float, int]


class Reader:
    def __init__(self, path: Union[str, Path], *args, **kwargs):
        self.path = Path(path)

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

    @overload
    def region(self, level: int, left: num, up: num, right: num, down: num, as_array: Literal[False] = True) -> np.ndarray:
        raise NotImplemented

    @overload
    def region(self, level: int, left: num, up: num, right: num, down: num, as_array: Literal[True] = False) -> Image:
        raise NotImplemented

    @abc.abstractmethod
    def region(self, level: int, left: num, up: num, right: num, down: num, as_array: bool = True):
        raise NotImplemented

    def thumb(self, level: int = -1) -> np.ndarray:
        level = level % self.level_count
        w, h = self.dimension(level)
        return self.region(level, 0, 0, w, h)

    def close(self):
        return self
