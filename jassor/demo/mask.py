import os
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
import jassor.utils as J
from jassor.components import Masking


def main():
    print('描述基本用法')
    # demo()
    # demo2()
    demo3()


def demo3():
    # image_root = Path(rf'../../resources/mm')
    image_root = Path(rf'../../resources/oj')
    images = []
    edges = []
    for image_path in [
        # '../../resources/test.jpg',
        # '../../resources/20250626134328.jpg',
        # '../../resources/code.png',
        *os.listdir(image_root)
    ]:
        image = np.asarray(Image.open(image_root / image_path))
        edge = Masking.get_sketch(image)
        # edge = Masking.get_edge2(image)
        images.append(image)
        edges.append(edge)
    J.plots([*images, *edges], ticks=False)


def demo2():
    image = cv2.cvtColor(cv2.imread('../../resources/test.jpg'), cv2.COLOR_BGR2RGB)
    # image = cv2.resize(image, (6000, 6000))
    valid = Masking.get_valid_area(image)
    J.plots([image, valid])


def demo():
    image = cv2.cvtColor(cv2.imread('../../resources/test.jpg'), cv2.COLOR_BGR2RGB)
    # 人像分割依赖深度学习模型权重，需要从网络上下载，需在此处指定下载后的保存位置
    human_mask = Masking.get_human(image, onnx_path='../../resources/modnet_photographic_portrait_matting.onnx')
    # 此分割用于滤除黑白灰类型的纯色区域，适用于显微识别方向，此处图片仅供参考
    # alpha 参数可以调节最大识别比率
    none_gray = Masking.get_none_gray(image, alpha=2)
    # 此分割可以扫描图像边缘区域，虽然我也不明白为什么
    # score_thresh 参数可以调节最大识别比率
    edge = Masking.get_edge(image)
    J.plots([image, human_mask, none_gray, edge])


if __name__ == '__main__':
    main()
