import cv2
import jassor.utils as J


def main():
    print('第一段程序展示傅里叶配准的效果')
    demo1()
    print('第二段程序展示关键点配准的效果')
    demo2()


def demo1():
    # 读取两幅图像
    image1 = cv2.imread(rf'../../resources/test.jpg', flags=cv2.IMREAD_GRAYSCALE)
    image1 = cv2.resize(image1, (801, 801))
    M = get_affine(10, 110, 30, 1.3, (400, 400))
    image2 = cv2.warpAffine(image1, M, (image1.shape[1], image1.shape[0]))
    dx, dy, degree, scale, reflect = J.align_fourier(image1, image2, return_matrix=False)
    print(dx, dy, degree, scale, reflect)
    J.plots([image1, image2], ticks=False)


def demo2():
    # 读取两幅图像
    image1 = cv2.imread(rf'../../resources/test.jpg', flags=cv2.IMREAD_GRAYSCALE)
    image1 = cv2.resize(image1, (801, 801))
    M = get_affine(10, 110, 30, 1.3, (400, 400))
    image2 = cv2.warpAffine(image1, M, (image1.shape[1], image1.shape[0]))
    dx, dy, degree, scale, reflect = J.align_keypoint(image1, image2, method='orb', return_matrix=False)
    print(dx, dy, degree, scale, reflect)
    J.plots([image1, image2], ticks=False)


def get_affine(dx, dy, degree, scale, center):
    # 参数定义
    # dx, dy = 0, 0  # 平移量
    # angle = 0  # 旋转角度（度数）
    # scale = 5  # 缩放比例
    # center = (400, 400)  # 旋转中心
    M = cv2.getRotationMatrix2D(center, degree, scale)
    M[0, 2] += dx
    M[1, 2] += dy
    return M


if __name__ == '__main__':
    main()
