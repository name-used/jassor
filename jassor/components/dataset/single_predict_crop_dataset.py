import abc
import random
from argparse import Namespace
from typing import List, Tuple, Dict, Any, Iterable, Union
from pathlib import Path
import cv2
import numpy as np
import torch
from collections import defaultdict
from .interface import Dataset as Interface
from .utils import check_slide, check_image, Slide


num = Union[int, float]


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
        return self.load(self.samples[item])

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def load(self, x: num, y: num, w: num, h: num) -> Any:
        """
        这里的复杂度在于：
        1. load 方法可能被多进程执行，若数据不共享，则每个子进程需要 copy 数据，而 io 管道不能被 copy
        2. image 与 slide 要采用相同的外部封装，但二者的代码逻辑完全不同
        """
        # 解析 sample 格式
        if isinstance(sample, tuple):
            image_id = 0
            left, up, right, down = sample
        elif isinstance(sample, dict):
            image_id = sample['image_id']
            left, up, right, down = sample['grid']
        else:
            raise TypeError('No such format supporting!')

        # 解析 str 路径
        image = self.source[image_id]
        if isinstance(image, (str, Path)) and check_slide(image):
            image = Slide(image)
            self.source[image_id] = image
        elif isinstance(image, (str, Path)) and check_image(image):
            image = cv2.cvtColor(cv2.imread(image), cv2.COLOR_BGR2RGB)
            self.source[image_id] = image
        else:
            pass
        # 加载图块
        if isinstance(image, np.ndarray):
            patch = image[up: down, left: right].copy()
        elif isinstance(image, Slide):
            patch = image.read_region(up, down, left, right)
        else:
            raise TypeError('No such type supporting!')

        return patch
