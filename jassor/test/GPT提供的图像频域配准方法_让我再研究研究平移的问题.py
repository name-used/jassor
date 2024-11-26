import cv2
import jassor.utils as J
import numpy as np
import matplotlib.pyplot as plt


def main():
    # 读取两幅图像
    img1 = cv2.imread(rf'C:\Users\jizhe\Pictures\test.jpg', cv2.IMREAD_GRAYSCALE)
    img1 = cv2.resize(img1, (801, 801))
    M = get_affine()
    img2 = cv2.warpAffine(img1, M, (img1.shape[1], img1.shape[0]))

    degree = cal_translate(img1, img2)
    print(degree)


def get_affine():
    # 参数定义
    angle = 0  # 旋转角度（度数）
    scale = 1  # 缩放比例
    tx, ty = 100, 200  # 平移量
    center = (400, 400)  # 旋转中心
    M = cv2.getRotationMatrix2D(center, angle, scale)
    M[0, 2] += tx
    M[1, 2] += ty
    return M


def cal_translate(img1: np.ndarray, img2: np.ndarray):
    fmg1 = np.fft.fft2(img1)
    fmg2 = np.fft.fft2(img2)
    cross_power_spectrum = np.fft.ifft2(fmg2 / fmg1)

    # J.plots([
    #     plt.cm.hsv(np.angle(fmg1) / np.pi / 2 + 0.5),
    #     plt.cm.hsv(np.angle(fmg2) / np.pi / 2 + 0.5),
    #     plt.cm.hsv(np.angle(fmg2 / fmg1) / np.pi / 2 + 0.5),
    #     np.abs(cross_power_spectrum),
    # ])

    cross_power_spectrum = np.abs(cross_power_spectrum)
    max_index = np.argmax(cross_power_spectrum)
    y, x = np.unravel_index(max_index, cross_power_spectrum.shape)
    return x, y


main()
