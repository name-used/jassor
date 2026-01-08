from typing import Tuple, Union
from pathlib import Path
import numpy as np
import tiffslide
from PIL.Image import Image
from .interface import Reader, num


class TiffSlide(Reader):
    def __init__(self, path: Union[str, Path]):
        super().__init__(path)
        self.slide = tiffslide.TiffSlide(str(self.path))

    @property
    def level_count(self) -> int:
        return self.slide.level_count

    @property
    def base_mpp(self) -> float:
        return float(self.slide.properties['tiffslide.mpp-x'])

    def dimension(self, level: int = 0) -> Tuple[int, int]:
        return self.slide.level_dimensions[level]

    def downsample(self, level: int = 0) -> float:
        return self.slide.level_downsamples[level]

    def region(self, level: int, left: num, up: num, right: num, down: num, as_array=True) -> Union[np.ndarray, Image]:
        downsample = self.downsample(level)
        l0 = round(left * downsample)
        u0 = round(up * downsample)
        w = round(right - left)
        h = round(down - up)
        patch = self.slide.read_region(location=(l0, u0), level=level, size=(w, h), as_array=as_array) # type: ignore[arg-type]
        return patch
