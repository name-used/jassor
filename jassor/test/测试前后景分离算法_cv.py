import torch
import numpy as np
import cv2
from models.modnet import MODNet
import jassor.utils as J


def main():
    # 读取图像
    img = cv2.imread('../../resources/test.jpg')

    # 加载预训练的 Deep Image Matting 模型
    # model = torch.load(rf'D:\jassorRepository\weights\MODNet\mobilenetv2_human_seg.ckpt')  # 替换为你下载的模型路径
    model = MODNet(backbone_arch='mobilenetv2', backbone_pretrained=False)
    model.load_state_dict(torch.load(rf'D:\jassorRepository\weights\MODNet\mobilenetv2_human_seg.ckpt'))
    model.to('cuda:0')
    model.eval()  # 设置为评估模式

    # 进行推断
    with torch.no_grad():
        output = model(img.to('cuda:0'))
    segmented_image = output[0].numpy()  # 获取前景部分
    segmented_image = (segmented_image * 255).astype(np.uint8)  # 转换为 0-255 范围内的值

    J.plots([img, segmented_image])


main()
