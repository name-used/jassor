import jassor.utils as J
import numpy as np
import cv2

width = 1920
height = 1080


def main():
    u = np.linalg.qr(np.random.randn(height, height))[0].astype(np.float32)
    v = np.linalg.qr(np.random.randn(width, width))[0].astype(np.float32)
    image = cv2.imread(rf'C:\Users\jizhe\Pictures\test.jpg', cv2.IMREAD_GRAYSCALE) / 255

    temp = u @ image @ v
    temp2 = temp.copy()

    convas = np.zeros_like(temp)
    cv2.putText(convas, 'hello', (256, 256), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=1, thickness=3)
    temp2[convas.astype(bool)] = 100

    result = u.T @ temp2 @ v.T
    # J.plots([image, result, temp, temp2])

    cut = np.zeros_like(result)
    cut[10:, 10:] = result[:-10, :-10]
    # cut = result

    logo = u @ cut @ v
    J.plots([image, result, cut, logo])


main()
