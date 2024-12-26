import numpy as np
import cv2
import jassor.utils as J


def main():
    print('第一段程序以矩阵为例展示效果')
    demo1()
    input('输入任意字符以继续...')
    print('第二段程序以图片为例展示效果')
    demo2()


def demo1():
    x = np.arange(100).reshape(10, 10)
    print(x)
    print(J.crop(x, (4.5, 4.5), (4, 4), degree=30, scale=1))
    print(J.crop(x, (4.5, 4.5), (4, 4), degree=30, scale=1, nearest=False))


def demo2():
    x = cv2.imread(rf'../../resources/test.jpg')
    J.plot(x)
    J.plot(J.crop(x, (960, 540), (400, 400), degree=30, scale=2))
    J.plot(J.crop(x, (960, 540), (400, 400), degree=30, scale=2, nearest=False))


if __name__ == '__main__':
    main()
