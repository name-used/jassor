import numpy as np
from typing import Tuple, Union
from pathlib import Path
from .interface import Reader, num


class NumpySlide(Reader):
    def __init__(self, path: Union[str, Path], base_mpp: float = 0.5):
        super().__init__(path)
        self.image = np.load(path)
        self.dim = len(self.image.shape)
        self._base_mpp = base_mpp

    @staticmethod
    def from_image(image: np.ndarray, path: Union[str, Path], mpp: float):
        slide = NumpySlide(path, mpp)
        slide.image = image
        return slide

    @property
    def level_count(self) -> int:
        return 1

    @property
    def base_mpp(self) -> float:
        return self._base_mpp

    def dimension(self, level: int = 0) -> Tuple[int, int]:
        h, w = self.image.shape[:2]
        return w, h

    def downsample(self, level: int = 0) -> float:
        return 1

    def region(self, level: int, left: num, up: num, right: num, down: num) -> np.ndarray:
        left = round(left)
        up = round(up)
        right = round(right)
        down = round(down)
        w, h = self.dimension()
        ml = max(0, left)
        mu = max(0, up)
        mr = min(w, right)
        md = min(h, down)
        patch = self.image[up: down, left: right]
        if ml == left and mu == up and mr == right and md == down:
            return patch.copy()
        patch = np.pad(patch, [(mu-up, down-md), (ml-left, right-mr), (0, 0)][:self.dim])
        return patch
