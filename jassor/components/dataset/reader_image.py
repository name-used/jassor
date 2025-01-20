from typing import Tuple
import numpy as np
from .interface import Reader, num
from PIL import Image
Image.MAX_IMAGE_PIXELS = 16_0000_0000


class ImageSlide(Reader):
    def __init__(self, image: Image.Image, base_mpp: float = 0.5):
        self.image = image
        self._base_mpp = base_mpp

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
