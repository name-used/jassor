import numpy as np
import matplotlib.pyplot as plt
from jassor.utils import random_rainbow_curves, random_colors


def main():
    print('第一段程序展示 random_colors 的效果')
    demo1()
    input('输入任意字符以继续...')
    print('第二段程序展示 random_rainbow_curves 的效果')
    demo2()


def demo1():
    x = random_colors(100)
    x = np.array(x)
    x = x.reshape((10, 10, 3))
    plt.imshow(x)
    plt.show()


def demo2():
    x = random_rainbow_curves((500, 500, 3), s=101)
    plt.imshow(x)
    plt.show()


if __name__ == '__main__':
    main()
