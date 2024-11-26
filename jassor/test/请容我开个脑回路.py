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

    # J.plots([img1, img2])

    scaling = detect_scaling_by_correlation(img1, img2)
    print(scaling)


def get_affine():
    # 参数定义
    angle = 0  # 旋转角度（度数）
    scale = 1  # 缩放比例
    tx, ty = 0, 0  # 平移量
    center = (400, 400)  # 旋转中心
    M = cv2.getRotationMatrix2D(center, angle, scale)
    M[0, 2] += tx
    M[1, 2] += ty
    return M


def detect_scaling_by_correlation(img1, img2):
    fmg1 = np.fft.fft2(img1)
    fmg2 = np.fft.fft2(img2)

    rfmg1 = xyf2rtf(fmg1)
    rfmg2 = xyf2rtf(fmg2)

    """通过互相关检测旋转角度"""
    # 计算互相关
    cross_corr = np.fft.ifft2(rfmg1 * rfmg2)
    cross_corr_shifted = np.fft.fftshift(cross_corr)

    J.plots([
        np.abs(fmg1).astype(np.float32),
        np.abs(fmg2).astype(np.float32),
        np.abs(cross_corr_shifted),
    ])

    # 找到互相关的峰值位置
    # r = np.abs(cross_corr_shifted).sum(axis=0).argmax()
    _, r = np.unravel_index(np.argmax(np.abs(cross_corr_shifted)), cross_corr_shifted.shape)

    # 计算缩放偏移
    scaling = r / rfmg1.shape[1]
    return scaling


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


def xyf2rtf(image: np.ndarray):
    a = image.real.astype(np.float32)
    b = image.imag.astype(np.float32)
    h, w = image.shape
    # 前面是双线性插值，后面是填充所有目标图像素
    flags = cv2.INTER_LINEAR | cv2.WARP_FILL_OUTLIERS
    # 圆心坐标
    center = (w / 2, h / 2)
    # center = (0, 0)
    # 圆的半径
    maxRadius = (h ** 2 + w ** 2) ** 0.5 / 2
    # linear Polar 极坐标变换, None表示OpenCV根据输入自行决定输出图像尺寸
    a = cv2.warpPolar(a, None, center, maxRadius, flags)
    b = cv2.warpPolar(b, None, center, maxRadius, flags)
    return a + 1j * b


main()
