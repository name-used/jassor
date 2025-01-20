from typing import Union, List
import numpy as np
import torch
import jassor.utils as J

std = [0.229, 0.224, 0.225]
mean = [0.485, 0.456, 0.406]


def trans_norm(target_input: Union[np.ndarray, torch.Tensor], channel_dim: int = 1):
    shape = [3 if i == channel_dim else 1 for i in range(len(target_input.shape))]
    m = np.asarray(mean).reshape(shape)
    s = np.asarray(std).reshape(shape)
    return (target_input / 255 - m) / s


def trans_linear(target_input: Union[np.ndarray, torch.Tensor]):
    return (target_input / 255 - 0.5) / 0.5


def sample_image(image: np.ndarray, kernel_size: int, step: int):
    h, w = image.shape[:2]
    k, s = kernel_size, step
    return [(x, y, x+k, y+k) for y in J.uniform_iter(h, k, s) for x in J.uniform_iter(w, k, s)]


def sample_slide(slide: Slide, kernel_size: int, step: int, base_mpp_or_downsample: float, ):
    pass
check_slide, check_image, Slide