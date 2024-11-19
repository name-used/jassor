import time
from typing import TextIO
import sys
import multiprocessing

import cv2
import numpy as np

import jassor.utils as J
from jassor.components import Marker


def main():
    print('第一段程序描述基本用法')
    demo1()
    # input('输入任意字符以继续...')
    # print('第二段程序拆解内置变换')
    # demo2()


def demo1():
    width = height = 256
    image = J.random_rainbow_curves((height, width, 3), s=13)
    image = (cv2.cvtColor(image, cv2.COLOR_RGB2GRAY).astype(np.float32) + 0.5) / 256
    m = Marker(width, height)
    # 按次序变换图像至目标域
    base = m.image(image).map().cross().dct().icross().imap().item()
    # 在目标域嵌入 logo
    mark = np.zeros_like(base)
    cv2.putText(mark, 'hello', (10, 156), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=1, thickness=3)
    mark = base + mark * 0.1
    # 逆变换回去
    result = m.mark(mark).map().cross().dct().icross().imap().item()
    J.plots([image, result, base, mark])

    # 操作结果图
    # destroy = result.copy()
    # destroy[50: 90, 30:110] = 1
    # mark = m.image(destroy).dct(t=3).cross().item()
    # J.plots([image, result, destroy, mark])


def demo2():
    pass


if __name__ == '__main__':
    main()
