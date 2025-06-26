import numpy as np
import cv2
from scipy.ndimage import uniform_filter
import torch

# img = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0)  # [1, 3, 6000, 6000]
# patches = img.unfold(2, 3, 1).unfold(3, 3, 1)  # [1, 3, 5998, 5998, 3, 3]
# patches = patches.permute(0, 2, 3, 1, 4, 5)  # [1, 5998, 5998, 3, 3, 3]
# patches = patches.squeeze(0)  # shape: (5998, 5998, 3, 3, 3)


def process(image: np.ndarray, s: int = 3, std_thresh: float = 5., b: int = 13, k: int = 17):
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

    # 再然后均值滤波扩散
    mask = uniform_filter(mask, size=(b, b))
    mask = uniform_filter(mask, size=(b, b))
    mask = uniform_filter(mask, size=(b, b))
    # 再阈值截断二值化
    mask = (mask > std_thresh).astype(np.uint8)
    # 最后做一个腐蚀膨胀
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    mask = cv2.dilate(mask, k, dst=mask, iterations=1)
    mask = cv2.erode(mask, k, dst=mask, iterations=2)
    mask = cv2.dilate(mask, k, dst=mask, iterations=1)
    return mask
