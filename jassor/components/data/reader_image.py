import numpy as np
from .interface import Reader, num
from PIL import Image
from typing import Tuple, Union
from pathlib import Path
Image.MAX_IMAGE_PIXELS = 16_0000_0000


class ImageSlide(Reader):
    def __init__(self, path: Union[str, Path], base_mpp: float = 0.5, force_convert: str = 'RGB'):
        super().__init__(path)
        self.image = Image.open(path)
        if force_convert:
            self.image = self.image.convert('RGB')
        self._base_mpp = base_mpp

    @staticmethod
    def from_image(image: Image, path: Union[str, Path], mpp: float):
        slide = ImageSlide(path, mpp)
        slide.image = image
        return slide

    @property
    def level_count(self) -> int:
        return 1

    @property
    def base_mpp(self) -> float:
        return self._base_mpp

    def dimension(self, level: int = 0) -> Tuple[int, int]:
        return self.image.size

    def downsample(self, level: int = 0) -> float:
        return 1

    def region(self, level: int, left: num, up: num, right: num, down: num) -> np.ndarray:
        patch = self.image.crop((left, up, right, down))
        return np.asarray(patch)
