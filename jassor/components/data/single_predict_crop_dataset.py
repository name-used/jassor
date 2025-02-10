from PIL import Image
from typing import List, Tuple, Any, Union
from pathlib import Path
import numpy as np
import torch
from .interface import Reader
from .reader import load
from .reader_numpy import NumpySlide
from .reader_image import ImageSlide


class SingleDataset(torch.utils.data.Dataset):
    """
    单图预测任务
    """
    def __init__(self, source: Union[str, Path, np.ndarray, Image.Image], samples: List[Tuple[int, int, int, int, int]]):
        super().__init__()
        self.source = source
        # [(level, left, up, right, down)]
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, item):
        return self.load(*self.samples[item])

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def load(self, level: int, left: int, up: int, right: int, down: int) -> Any:
        """
        这里的复杂度在于：
        1. load 方法可能被多进程执行，若数据不共享，则每个子进程需要 copy 数据，而 io 管道不能被 copy
        2. image 与 slide 要采用相同的外部封装，但二者的代码逻辑完全不同
        """
        # 解析路径
        if isinstance(self.source, Reader):
            pass
        elif isinstance(self.source, (str, Path)):
            self.source = load(self.source)
        elif isinstance(self.source, Image.Image):
            self.source = ImageSlide(self.source)
        elif isinstance(self.source, np.ndarray):
            self.source = NumpySlide(self.source)
        else:
            raise TypeError(f'No such type supporting! {type(self.source)}')
        return self.source.region(level=level, left=left, up=up, right=right, down=down)
