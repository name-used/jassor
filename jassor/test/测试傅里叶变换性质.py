import cv2
import jassor.utils as J
import numpy as np
import matplotlib.pyplot as plt


def main():
    # 读取两幅图像
    img1 = cv2.imread(rf'C:\Users\jizhe\Pictures\test.jpg', cv2.IMREAD_GRAYSCALE)
    M = get_affine()
    img2 = cv2.warpAffine(img1, M, (img1.shape[1], img1.shape[0]))
    fmg1 = np.fft.fftshift(np.fft.fft2(img1))
    fmg2 = np.fft.fftshift(np.fft.fft2(img2))

    J.plots([
        img1, img2,
        np.log(abs(fmg1)),
        np.log(abs(fmg2)),
    ])


def get_affine():
    # 参数定义
    angle = 45  # 旋转角度（度数）
    scale = 1  # 缩放比例
    tx, ty = 0, 0  # 平移量
    center = (960, 540)  # 旋转中心
    M = cv2.getRotationMatrix2D(center, angle, scale)
    M[0, 2] += tx
    M[1, 2] += ty
    return M


def xy2rt(image: np.ndarray):
    h, w = image.shape
    # 前面是双线性插值，后面是填充所有目标图像素
    flags = cv2.INTER_LINEAR | cv2.WARP_FILL_OUTLIERS
    # 圆心坐标
    center = (w / 2, h / 2)
    # center = (0, 0)
    # 圆的半径
    maxRadius = (h ** 2 + w ** 2) ** 0.5 / 2
    # linear Polar 极坐标变换, None表示OpenCV根据输入自行决定输出图像尺寸
    polar_img = cv2.warpPolar(image, None, center, maxRadius, flags)
    return polar_img


main()
