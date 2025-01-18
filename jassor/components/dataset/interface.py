import abc
import random
from typing import List, Tuple, Dict, Any
import numpy as np
import torch


class Dataset(torch.utils.data.Dataset, abc.ABC):

    def __init__(self, samples: List[Dict[str, Any]]):
        super().__init__()
        self.samples = samples

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, item):
        return self.load(self.samples[item])

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    @abc.abstractmethod
    def load(self, sample) -> Any: pass
