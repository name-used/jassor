import numpy as np


def cut_label(label: np.ndarray, l: int, u: int, r: int, d: int, ignore: int = 5, MIN: int = -999_999_999) -> np.ndarray:
    # label = array([(l, u, r, d)], dtype=(float, int))
    # assert label > 0
    if len(label) == 0: return label

    label = label.copy()

    # choose in box
    label[label[:, 0] >= r - ignore, 0] = MIN  # label at box right
    label[label[:, 1] >= d - ignore, 1] = MIN  # label at box down
    label[label[:, 2] <= l + ignore, 2] = MIN  # label at box left
    label[label[:, 3] <= u + ignore, 3] = MIN  # label at box up
    label = label[label.sum(axis=1) > 0, :]

    # limit to box
    label[label[:, 0] < l, 0] = l
    label[label[:, 1] < u, 1] = u
    label[label[:, 2] > r, 2] = r
    label[label[:, 3] > d, 3] = d

    # absolute -> relative
    label[:, (0, 2)] -= l
    label[:, (1, 3)] -= u

    # [t, l, u, r, d] :: [0 - w/h]
    return label
