from PIL import Image
from typing import List, Tuple, Any, Union
from pathlib import Path
import numpy as np
import torch
from .reader import load, ImageLoader


class SingleDataset(torch.utils.data.Dataset):
    """
    单图预测任务
    """
    def __init__(self, source: Union[str, Path, np.ndarray], samples: List[Tuple[int, int, int, int]]):
        # samples = [defaultdict(lambda: 0, **sample) for sample in samples]
        super().__init__()
        self.source = source
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, item):
        return self.load(*self.samples[item])

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def load(self, level: int, left: int, up: int, width: int, height: int) -> Any:
        """
        这里的复杂度在于：
        1. load 方法可能被多进程执行，若数据不共享，则每个子进程需要 copy 数据，而 io 管道不能被 copy
        2. image 与 slide 要采用相同的外部封装，但二者的代码逻辑完全不同
        """
        # 解析路径
        if isinstance(self.source, (str, Path)):
            self.source = load(self.source)
        elif isinstance(self.source, (Image.Image, np.ndarray)):
            self.source = ImageLoader(self.source)
        else:
            raise TypeError(f'No such type supporting! {type(self.source)}')
        return self.source.read_region(location=(left, up), level=level, size=(width, height))

        # if isinstance(self.source, (str, Path)) and check_slide(self.source):
        #     self.source = Slide(self.source)
        # elif isinstance(self.source, (str, Path)) and check_image(self.source):
        #     self.source = np.asarray(Image.open(self.source).convert('RGB'))
        # else:
        #     pass
        # # 加载图块
        # if isinstance(self.source, np.ndarray):
        #     patch = self.source[u: d, l: r].copy()
        # elif isinstance(self.source, Slide):
        #     patch =
        # else:
        #     raise TypeError('No such type supporting!')
