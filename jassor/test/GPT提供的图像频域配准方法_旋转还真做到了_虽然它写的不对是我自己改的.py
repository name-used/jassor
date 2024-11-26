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

    degree = detect_rotation_angle_by_correlation(img1, img2)
    print(degree)

    # fmg1 = np.fft.fft2(img1)
    # fmg2 = np.fft.fft2(img2)
    #
    # jassor.utils.plots([
    #     img1, img2,
    #     np.log(abs(fmg1) + 1e-19), np.log(abs(fmg2) + 1e-19),
    #     plt.cm.hsv(np.angle(fmg1) / np.pi / 2 + 0.5),
    #     plt.cm.hsv(np.angle(fmg2) / np.pi / 2 + 0.5),
    # ])

    # 调用频域方法估计变换
    # tx, ty = cal_translate(fmg1, fmg2)

    # print(f"Estimated Translation: ({tx}, {ty})")


def get_affine():
    # 参数定义
    angle = 71  # 旋转角度（度数）
    scale = 1  # 缩放比例
    tx, ty = 0, 0  # 平移量
    center = (400, 400)  # 旋转中心
    M = cv2.getRotationMatrix2D(center, angle, scale)
    M[0, 2] += tx
    M[1, 2] += ty
    return M


def detect_rotation_angle_by_correlation(mag_orig, mag_rot):

    mag_orig = xy2rt(mag_orig)
    mag_rot = xy2rt(mag_rot)

    """通过互相关检测旋转角度"""
    # 计算互相关
    cross_corr = np.fft.ifft2(np.fft.fft2(mag_orig) * np.conj(np.fft.fft2(mag_rot)))
    cross_corr_shifted = np.fft.fftshift(cross_corr)

    # J.plots([
    #     mag_orig,
    #     mag_rot,
    #     np.abs(cross_corr_shifted),
    #     plt.cm.hsv(np.angle(cross_corr_shifted) / np.pi / 2 + 0.5)
    # ])

    # 找到互相关的峰值位置
    max_loc = np.unravel_index(np.argmax(np.abs(cross_corr_shifted)), cross_corr_shifted.shape)

    # 计算角度偏移
    angle = (max_loc[0] - mag_orig.shape[0] // 2) * 360 / mag_orig.shape[0]
    # angle = max_loc[0] * 360 / mag_orig.shape[0]
    return angle


def xy2rt(image: np.ndarray):
    h, w = image.shape
    # 前面是双线性插值，后面是填充所有目标图像素
    flags = cv2.INTER_LINEAR | cv2.WARP_FILL_OUTLIERS
    # 圆心坐标
    center = (w / 2, h / 2)
    # center = (0, 0)
    # 圆的半径
    maxRadius = (h ** 2 + w ** 2) ** 0.5
    # linear Polar 极坐标变换, None表示OpenCV根据输入自行决定输出图像尺寸
    polar_img = cv2.warpPolar(image, None, center, maxRadius, flags)
    return polar_img


# def cal_translate(fmg1: np.ndarray, fmg2: np.ndarray):
#     cross_power_spectrum = np.fft.ifft2(fmg2 / fmg1)
#     cross_power_spectrum = np.abs(cross_power_spectrum)
#     max_index = np.argmax(cross_power_spectrum)
#     y, x = np.unravel_index(max_index, cross_power_spectrum.shape)
#     return x, y


def cal_translate(fmg1: np.ndarray, fmg2: np.ndarray):
    cross_power_spectrum = np.fft.ifft2(fmg2 / fmg1)
    cross_power_spectrum = np.abs(cross_power_spectrum)
    max_index = np.argmax(cross_power_spectrum)
    y, x = np.unravel_index(max_index, cross_power_spectrum.shape)
    return x, y


def estimate_transform(img1, img2):
    # 1. 对两幅图像做傅里叶变换
    fft1 = np.fft.fft2(img1)
    fft2 = np.fft.fft2(img2)

    # 2. 提取幅值谱（忽略相位）
    magnitude1 = np.abs(fft1)
    magnitude2 = np.abs(fft2)

    # 3. 对幅值谱做对数变换（避免动态范围过大）
    log_mag1 = np.log1p(magnitude1)
    log_mag2 = np.log1p(magnitude2)

    # 4. 将幅值谱转换为对数极坐标
    center = (log_mag1.shape[1] // 2, log_mag1.shape[0] // 2)  # 图像中心
    polar1 = cv2.warpPolar(log_mag1, (360, log_mag1.shape[0]), center, center[0], cv2.WARP_POLAR_LOG)
    polar2 = cv2.warpPolar(log_mag2, (360, log_mag2.shape[0]), center, center[0], cv2.WARP_POLAR_LOG)

    # 5. 计算旋转和缩放
    # 使用相位相关计算极坐标下的匹配
    cross_power_spectrum = np.fft.ifft2(np.fft.fft2(polar1) * np.conj(np.fft.fft2(polar2)))
    max_loc = np.unravel_index(np.argmax(np.abs(cross_power_spectrum)), cross_power_spectrum.shape)
    rotation = max_loc[1] * 360 / polar1.shape[1]  # 角度
    scale = np.exp(max_loc[0] / polar1.shape[0])  # 缩放比例

    # 6. 将旋转和缩放应用于图像 B
    M = cv2.getRotationMatrix2D(center, -rotation, scale)
    adjusted_img2 = cv2.warpAffine(img2, M, (img1.shape[1], img1.shape[0]))

    # 7. 再次计算平移
    cross_power_spectrum = np.fft.ifft2(np.fft.fft2(img1) * np.conj(np.fft.fft2(adjusted_img2)))
    max_loc = np.unravel_index(np.argmax(np.abs(cross_power_spectrum)), cross_power_spectrum.shape)
    tx, ty = max_loc[1], max_loc[0]  # 平移量

    return rotation, scale, tx, ty


main()
