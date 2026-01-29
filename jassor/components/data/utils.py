import math
from typing import Union, List, Tuple, Literal
import PIL.Image
import numpy as np
import jassor.utils as J
from .interface import Reader

std = np.asarray([0.229, 0.224, 0.225])
mean = np.asarray([0.485, 0.456, 0.406])


def trans_norm(target_input: np.ndarray, channel_dim: int = 1) -> np.ndarray:
    shape = [3 if i == channel_dim else 1 for i in range(len(target_input.shape))]
    m = mean.reshape(shape)
    s = std.reshape(shape)
    return (target_input / 255 - m) / s


def trans_linear(target_input: np.ndarray) -> np.ndarray:
    return (target_input / 255 - 0.5) / 0.5


def sample_image(image: Union[np.ndarray, PIL.Image.Image], kernel_size: int, step: int) -> List[Tuple[int, int, int, int, int]]:
    w, h = image.shape[:2][::-1] if isinstance(image, np.ndarray) else image.size
    k, s = kernel_size, step
    # image 的 level 恒为 0
    return [(0, x, y, x+k, y+k) for y in J.uniform_iter(h, k, s) for x in J.uniform_iter(w, k, s)]


def sample_slide(reader: Reader, level: int, kernel_size: int, step: int, mask: np.ndarray = None) -> List[Tuple[int, int, int, int, int]]:
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


MODE = Literal["overshoot", "in_bounds", "uniform"]


def find_sites(sight: Tuple[int, int, int, int], k: int, s: int, mode: MODE = 'uniform', mask: np.ndarray = None) -> List[Tuple[int, int]]:
    """
    在指定视野内进行坐标采样，支持两种采样模式，支持基于 mask 的组织区域过滤模式
    :param sight:   采样视野，必要参数，确立待采样坐标点的空间范围
    :param k:       采样窗口尺寸
    :param s:       采样步长
    :param mode:    采样模式，有三种候选："overshoot", "in_bounds", "uniform"
                    overshoot - 越界模式，采样点会最终越过 sight，以保证 sight 内的所有点都被采集到
                    in_bounds - 保留模式，采样点会保持在 sight 之内，但不保证 sight 内的所有点都被采集到
                    uniform - 密铺模式，采样点会恰好采集完 sight 内的所有点，并在此基础之上尽量保证采样的均衡性，但不保证步长仍然是 s（保证不大于 s）
    :param mask:    采样过滤矩阵（通常是降采样的），要求 mask 恰好与 sight 保持一致
    :return:        grids = [(left, up)]
    """
    sl, su, sr, sd = sight
    if mode == 'overshoot':
        grids = [(x, y) for y in range(su, sd - k + s, s) for x in range(sl, sr - k + s, s)]
    elif mode == 'in_bounds':
        grids = [(x, y) for y in range(su, sd - k + 1, s) for x in range(sl, sr - k + 1, s)]
    elif mode == 'uniform':
        grids = [(sl + x, su + y) for y in J.uniform_iter(sd - su, k, s) for x in J.uniform_iter(sr - sl, k, s)]
    else:
        raise ValueError(rf'Unexpected mode: {mode!r}. Expected one of ["overshoot", "in_bounds", "uniform"]')
    if mask is None:
        return grids
    W, H = sr - sl, sd - su
    h, w = mask.shape
    new_grids = []
    for x, y in grids:
        l = math.floor((x - sl) * w / W)
        u = math.floor((y - su) * h / H)
        r = math.ceil((x + k - sl) * w / W)
        d = math.ceil((y + k - su) * h / H)
        if mask[u: d+1, l: r+1].any():
            new_grids.append((x, y))
    return new_grids
