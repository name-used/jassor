import os
from pathlib import Path
from PIL import Image
import numpy as np
import cv2
import jassor.utils as J
from jassor.components import Masking


def main():
    print('展示多种分割方法的效果')
    demo()
    print('展示 valid 方法的效果')
    demo2()
    print('在 resources/sketches 放置一些你喜欢的图片，然后展示 sketch 方法的效果（素描画）')
    demo3()


def demo():
    # 'get_human'
    # 'get_none_gray'
    # 'get_edge'
    # 'get_edge2'
    # 'get_valid'
    # 'get_sketch'
    image = cv2.cvtColor(cv2.imread('../../resources/test.jpg'), cv2.COLOR_BGR2RGB)
    # 人像分割依赖深度学习模型权重，需要从网络上下载，需在此处指定下载后的保存位置
    human_mask = Masking.get_human(image, onnx_path='../../resources/modnet_photographic_portrait_matting.onnx')
    # 此分割用于滤除黑白灰类型的纯色区域，适用于显微识别方向，此处图片仅供参考
    # alpha 参数可以调节最大识别比率
    none_gray = Masking.get_none_gray(image, alpha=2)
    # 此分割可以扫描图像边缘区域，虽然我也不明白为什么
    edge = Masking.get_edge(image)
    # 此分割倒是专门扫描图像边缘区域用的
    # edge2 = Masking.get_edge2(image)
    # 此分割用于提取复杂信息密度区域（适用于病理图像 HE 染色）
    # valid = Masking.get_valid(image)
    # 此分割是专门的素描画生成器
    # sketch = Masking.get_sketch(image)
    J.plots([image, human_mask, none_gray, edge])


def demo2():
    image = cv2.cvtColor(cv2.imread('../../resources/test.jpg'), cv2.COLOR_BGR2RGB)
    valid = Masking.get_valid(image)
    J.plots([image, valid])


def demo3():
    image_root = Path(rf'../../resources/sketches')
    images = []
    edges = []
    for image_path in os.listdir(image_root):
        image = np.asarray(Image.open(image_root / image_path))
        edge = Masking.get_sketch(image)
        # edge = Masking.get_edge2(image)
        images.append(image)
        edges.append(edge)
    J.plots([*images, *edges], ticks=False)


if __name__ == '__main__':
    main()
