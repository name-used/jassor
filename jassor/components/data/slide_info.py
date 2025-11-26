from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import tifffile


@dataclass
class SlideInfo:
    """只负责描述“文件里真实存的形制”"""
    dtype: np.dtype
    channels: int          # 0->[H,W]; 1->[H,W,1]; 3/4->[H,W,C]
    mode: Optional[str]    # 'GRAY' / 'RGB' / 'RGBA' / None
    shape: Tuple[int, ...] # level 对应的完整 shape

    @property
    def color(self):
        """满足你说的 slide.color 接口：能解析就返回字符串，否则返回通道数."""
        return self.mode if self.mode is not None else self.channels


def _infer_channels_and_mode(shape: Tuple[int, ...]) -> Tuple[int, Optional[str]]:
    """根据 TIFF 的 shape 推断通道数和颜色模式."""
    # 典型 WSI： (H, W) 或 (H, W, C)
    if len(shape) == 2:
        # 纯 2D，没有显式通道轴 -> 你要求用 0 表示 [H, W]
        return 0, 'GRAY'   # 这里可以认为是灰度

    if len(shape) == 3:
        h, w, c = shape
        # 标准 [H, W, C]
        if c in (1, 3, 4):
            if c == 1:
                return 1, 'GRAY'
            if c == 3:
                return 3, 'RGB'
            if c == 4:
                return 4, 'RGBA'
        # 一些 OME-TIFF 可能是 [C, H, W]
        c = shape[0]
        if c in (1, 3, 4):
            if c == 1:
                return 1, 'GRAY'
            if c == 3:
                return 3, 'RGB'
            if c == 4:
                return 4, 'RGBA'
        # 奇怪的情况：就把最后一维当通道，但不给模式名
        return shape[-1], None

    # 更高维（比如 TCZYX）这里就不强行解了，只给个通道数
    return shape[-1], None


def get_slide_info(path) -> SlideInfo:
    """
    只读 TIFF/SVS 头部，不解压像素，嗅探存储 dtype + 通道数.
    """
    path = str(Path(path))
    with tifffile.TiffFile(path) as tf:
        s = tf.series[0]
        # 多层金字塔：series.levels 是各 level 的 view
        if getattr(s, "levels", None):
            page = s.levels[0]
        else:
            page = s

        dtype = page.dtype
        shape = page.shape

    channels, mode = _infer_channels_and_mode(shape)
    return SlideInfo(dtype=dtype, channels=channels, mode=mode, shape=shape)
