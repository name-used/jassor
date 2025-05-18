from typing import Tuple, Union
from pathlib import Path
import numpy as np
import multiresolutionimageinterface as mir
from .interface import Reader, num


class AsapSlide(Reader):
    def __init__(self, path: Union[str, Path]):
        self.slide = mir.MultiResolutionImageReader().open(path)

    @property
    def level_count(self) -> int:
        return self.slide.getNumberOfLevels()

    @property
    def base_mpp(self) -> float:
        return float(self.slide.getProperty('openslide.mpp-x'))

    def dimension(self, level: int = 0) -> Tuple[int, int]:
        return self.slide.getLevelDimensions(level % self.level_count)

    def downsample(self, level: int = 0) -> float:
        return self.slide.getLevelDownsample(level % self.level_count)

    def region(self, level: int, left: num, up: num, right: num, down: num) -> np.ndarray:
        downsample = self.downsample(level)
        l0 = round(left * downsample)
        u0 = round(up * downsample)
        w = round(right - left)
        h = round(down - up)
        patch = self.slide.getUCharPatch(startX=l0, startY=u0, width=w, height=h, level=level)
        return patch
