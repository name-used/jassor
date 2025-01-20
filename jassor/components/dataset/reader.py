import os.path
from typing import Union
from pathlib import Path
import numpy as np
from PIL import Image

SlideType = None
try:
    from reader_openslide import OpenSlide
    SlideType = OpenSlide
except ImportError:
    try:
        from reader_asap import AsapSlide
        SlideType = AsapSlide
    except ImportError:
        try:
            from reader_tiff import TiffSlide
            SlideType = TiffSlide
        except ImportError:
            pass


def load(path: Union[str, Path]):
    _, ext = os.path.splitext(path)
    if ext in ('.png', '.jpg', 'jpeg'):
        return ImageLoader(Image.open(path).convert('RGB'))
    if ext in ('.tif', '.svs'):
        if SlideType is None:
            raise ImportError('Lib Imported Failed!')
        return Slide(path, type=SlideType)
    raise TypeError(f'File type not supported! {ext}')


class ImageLoader:
    def __init__(self, image: Image.Image):
        self.image = np.asarray(image)


class SlideLoader:
    def __init__(self, image: Image.Image):
        self.image = np.asarray(image)
