import cv2
import jassor.utils as J
import jassor.shape as S


def main():
    image = J.random_rainbow_curves((1000, 1000, 3))
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mask = gray > 100
    contour: S.Shape = J.find_contour(mask)
    J.plots([image, gray, mask, contour.flip_y(0)], ticks=False)


if __name__ == '__main__':
    main()
