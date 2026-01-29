import cv2
from pathlib import Path

import numpy as np

import jassor.utils as J
from jassor.components import Marker


path = Path(rf'../../resources/car.jpg')


def main():
    image = cv2.imread(str(path))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    h, w, _ = image.shape
    h, w = h * 2, w * 2
    image = cv2.resize(image, (w, h))
    core = Marker.map_to(image[..., 0])
    canvas = np.zeros_like(core[7::8, 7::8]).astype(np.uint8)
    cv2.putText(canvas, 'VA', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, 1)
    mixed = core.copy()
    mixed[7::8, 7::8] += canvas
    image[..., 0] = Marker.imap_to(mixed)[:h, :w]

    core = np.log(abs(core) + 1).clip(0, 1) * np.sign(core)
    mixed = np.log(abs(mixed) + 1).clip(0, 1) * np.sign(mixed)
    check = Marker.map_to(image[..., 0])
    check = np.log(abs(check) + 1).clip(0, 1) * np.sign(check)
    J.plots([image, canvas, core[7::8, 7::8], mixed[7::8, 7::8], check[7::8, 7::8]])


main()
