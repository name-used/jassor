import json

import cv2
import jassor.utils as J
import jassor.shape as S


def main():
    demo2()


def demo2():
    with open('../../resources/1.geojson') as f:
        geojson = json.load(f)
    shapes = J.geojson2shapes(geojson)
    for item in shapes:
        print(item.keys(), item['shape_type'])
        J.plot(item['shape'])


def demo1():
    image = J.random_rainbow_curves((1000, 1000, 3))
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mask = gray > 100
    contour: S.Shape = J.find_contour(mask)
    J.plots([image, gray, mask, contour.flip_y(0)], ticks=False)


if __name__ == '__main__':
    main()
