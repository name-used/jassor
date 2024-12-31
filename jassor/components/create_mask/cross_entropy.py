import cv2
import numpy as np
from skimage import measure
from skimage.measure import regionprops
from copy import deepcopy
from scipy.signal import argrelextrema
from skimage.filters.rank import entropy
from skimage.morphology import disk


def process(image: np.ndarray):
    if len(image.shape) == 2:
        pass
    if image.shape[2] == 1:
        image = image[:, :, 0]
    elif image.shape[2] == 3:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    elif image.shape[2] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)

    source = deepcopy(image)
    ent = entropy(source, disk(5))
    hist = list(np.histogram(ent, 30))
    minindex = list(argrelextrema(hist[0], np.less))

    thresh_localminimal = 0
    for i in range(len(minindex[0])):
        temp_thresh = hist[1][minindex[0][i]]
        if 1 < temp_thresh < 4:
            thresh_localminimal = temp_thresh

    eimage = entropy(image, disk(3))
    new_picture = np.ndarray(shape=eimage.shape)  # [[False] * image.shape[1]] * image.shape[0]
    for rn, row in enumerate(eimage):
        for pn, pixel in enumerate(row):
            if pixel < thresh_localminimal:
                new_picture[rn, pn] = True
            else:
                new_picture[rn, pn] = False
    entropy_image = new_picture.astype('b')

    thresh1 = (255 * entropy_image).astype('uint8')
    mask_255 = cv2.bitwise_not(deepcopy(thresh1))

    redolbl = measure.label(np.array(mask_255), connectivity=2)
    redprops = regionprops(redolbl)

    redAreaData = []
    for r in range(len(redprops)):
        redAreaData.append(redprops[r].area)

    # 新方法
    redAreaData = sorted(enumerate(redAreaData), key=lambda p: p[1], reverse=True)
    # choses = [i for i, v in redAreaData]
    choses = []
    for i, v in redAreaData:
        if v > 0 and v / sum(p[1] for p in redAreaData[:i+1]) > 0.005:
            choses.append(i)
        else:
            break
    max_mask = np.zeros_like(image)
    for chose in choses:
        max_mask[redolbl == chose + 1] = 255

    return max_mask
