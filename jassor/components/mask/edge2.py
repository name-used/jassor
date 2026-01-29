import numpy as np
import torch


def process(image: np.ndarray, s: int = 3, pmin: int = 0, pmax: int = 100):
    # 手动扩圈
    image = np.pad(image, [(1, 1), (1, 1), (0, 0)])
    image[0, :, :] = image[1, :, :]
    image[-1, :, :] = image[-2, :, :]
    image[:, 0, :] = image[:, 1, :]
    image[:, -1, :] = image[:, -2, :]
    # 在局部计算 std，unfold 三个参数：dim，kernel，step
    with torch.no_grad():
        mask = torch.from_numpy(image).unfold(0, s, 1).unfold(1, s, 1)
        mask = mask.type(torch.float32).std(dim=(3, 4))
        mask = mask.mean(dim=2).numpy()

    pmin = np.percentile(mask, pmin)
    pmax = np.percentile(mask, pmax)
    mask = (mask - pmin) / (pmax - pmin + 1e-19)
    mask = mask.clip(0, 1) * 255
    mask = mask.astype(np.uint8)

    return mask
