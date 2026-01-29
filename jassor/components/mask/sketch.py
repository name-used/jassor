import cv2
import numpy as np


def process(image: np.ndarray, blur_size: int = 9, thresh_min: float = 0, thresh_max: float = 1.):
    # unify image channels to 3
    if len(image.shape) == 2:
        image = image[:, :, None]
    if image.shape[2] == 1:
        image = np.repeat(image, 3, axis=2)
    elif image.shape[2] == 4:
        image = image[:, :, 0: 3]
    image = image / 255
    blurred = cv2.GaussianBlur(image, (blur_size, blur_size), sigmaX=0, sigmaY=0)
    divided = (image + 0.01) / (blurred + 0.01)
    mask = divided
    # mask = np.where(divided < 1, divided, 1 / divided)
    mask = mask.clip(thresh_min, thresh_max)
    mask -= thresh_min
    mask /= thresh_max - thresh_min
    mask = (mask * 255).round().astype(np.uint8)

    return mask
