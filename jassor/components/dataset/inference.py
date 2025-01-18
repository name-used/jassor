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


class InferenceDataset(Interface):
    """
    推理数据集不需要处理复杂的 label 变换，与训练/验证数据集差别最大，因此
    单列
    数据集本身不处理采样问题，采样可以用采样工具实现
    """
    def __init__(self, *source: Iterable[Union[str, Path, np.ndarray]], samples: List[Union[Tuple[int, int, int, int], Dict[str, Any]]]):
        # samples = [defaultdict(lambda: 0, **sample) for sample in samples]
        super().__init__(samples)
        self.source = list(source)

    def load(self, sample) -> Any:
        """
        这里的复杂度在于：
        1. load 方法可能被多进程执行，若数据不共享，则每个子进程需要 copy 数据，而 io 管道不能被 copy
        2. image 与 slide 要采用相同的外部封装，但二者的代码逻辑完全不同
        3. images 既有可能是单图封装，也有可能是多图封装，理论上一图一过效率较低，但外部使用起来代码简洁
        4.
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
