import math
from typing import Union

import PIL.Image
import numpy as np
import torch
import jassor.utils as J
from .interface import Reader

std = np.asarray([0.229, 0.224, 0.225])
mean = np.asarray([0.485, 0.456, 0.406])


def trans_norm(target_input: Union[np.ndarray, torch.Tensor], channel_dim: int = 1):
    shape = [3 if i == channel_dim else 1 for i in range(len(target_input.shape))]
    m = mean.reshape(shape)
    s = std.reshape(shape)
    return (target_input / 255 - m) / s


def trans_linear(target_input: Union[np.ndarray, torch.Tensor]):
    return (target_input / 255 - 0.5) / 0.5


def sample_image(image: Union[np.ndarray, PIL.Image.Image], kernel_size: int, step: int):
    w, h = image.shape[:2][::-1] if isinstance(image, np.ndarray) else image.size
    k, s = kernel_size, step
    # image 的 level 恒为 0
    return [(0, x, y, x+k, y+k) for y in J.uniform_iter(h, k, s) for x in J.uniform_iter(w, k, s)]


def sample_slide(reader: Reader, level: int, kernel_size: int, step: int, mask: np.ndarray = None):
    W, H = reader.dimension(level)
    k, s = kernel_size, step
    if mask is not None:
        basic_samples = [(x, y, x+k, y+k) for y in J.uniform_iter(H, k, s) for x in J.uniform_iter(W, k, s)]
        h, w = mask.shape[:2]
        mask_samples = [[math.floor(l*w/W), math.floor(u*h/H), math.ceil(r*w/W), math.ceil(d*h/H)] for l, u, r, d in basic_samples]
        filtered_samples = [
            (level, l, u, r, d) for (l, u, r, d), (ml, mu, mr, md) in zip(basic_samples, mask_samples)
            if mask[mu: md, ml: mr].any()
        ]
        return filtered_samples
    else:
        return [(level, x, y, x+k, y+k) for y in J.uniform_iter(H, k, s) for x in J.uniform_iter(W, k, s)]
