import cv2
import jassor.utils as J
from jassor.components import Masking


def main():
    print('描述基本用法')
    demo()


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
