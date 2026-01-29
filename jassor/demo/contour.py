import json

import cv2
import jassor.utils as J
import jassor.shape as S


def main():
    demo1()
    # demo2()


def demo2():
    with open('../../resources/1.geojson') as f:
        geojson = json.load(f)
    shapes, props = S.convert_geojson2shapes(geojson)
    for shape, prop in zip(shapes, props):
        print(prop.keys(), shape)
        J.plot(shape)


def demo1():
    image = J.random_rainbow_curves((1000, 1000, 3))
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mask = gray > 100
    contour: S.Shape = S.convert_mask2shape(mask)
    J.plots([image, gray, mask, contour.flip_y(0)], ticks=False)


if __name__ == '__main__':
    main()
