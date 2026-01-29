import os.path
from pathlib import Path
from typing import Union, Optional, Type

from .reader_image import ImageSlide
from .reader_numpy import NumpySlide

SlideType: Optional[Type] = None

for _import in (
        lambda: __import__(__name__.rsplit(".", 1)[0] + ".reader_openslide", fromlist=["OpenSlide"]).OpenSlide,
        lambda: __import__(__name__.rsplit(".", 1)[0] + ".reader_asap", fromlist=["AsapSlide"]).AsapSlide,
        lambda: __import__(__name__.rsplit(".", 1)[0] + ".reader_tiff", fromlist=["TiffSlide"]).TiffSlide,
):
    try:
        SlideType = _import()
        break
    except ImportError:
        pass


def load(path: Union[str, Path]):
    _, ext = os.path.splitext(path)
    if ext in ('.png', '.jpg', '.jpeg'):
        return ImageSlide(path)
    if ext in ('.tif', '.svs'):
        if SlideType is None:
            raise ImportError('Lib Imported Failed!')
        return SlideType(path)
    if ext in ('.numpy',):
        return NumpySlide(path)
    raise TypeError(f'File type not supported! {ext}')
