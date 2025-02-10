from typing import Tuple, Union
from pathlib import Path
import numpy as np
import openslide
from .interface import Reader, num


class OpenSlide(Reader):
    def __init__(self, path: Union[str, Path]):
        self.slide = openslide.OpenSlide(path)

    @property
    def level_count(self) -> int:
        return self.slide.level_count

    @property
    def base_mpp(self) -> float:
        return float(self.slide.properties['openslide.mpp-x'])

    def dimension(self, level: int = 0) -> Tuple[int, int]:
        return self.slide.level_dimensions[level]

    def downsample(self, level: int = 0) -> float:
        return self.slide.level_downsamples[level]

    def region(self, level: int, left: num, up: num, right: num, down: num) -> np.ndarray:
        downsample = self.downsample(level)
        l0 = round(left * downsample)
        u0 = round(up * downsample)
        w = round(right - left)
        h = round(down - up)
        patch = self.slide.read_region(location=(l0, u0), level=level, size=(w, h))
        return np.asarray(patch)
