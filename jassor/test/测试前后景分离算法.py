import torch
import numpy as np
import cv2
from PIL import Image
import torchvision.transforms as transforms
import jassor.utils as J


def main():
    # 读取图像
    img = cv2.imread('../../resources/test.jpg')

    # 加载预训练的 Deep Image Matting 模型
    model = torch.load(rf'D:\jassorRepository\weights\vgg16_weights_tf_dim_ordering_tf_kernels.h5')  # 替换为你下载的模型路径
    model.to('cuda:0')
    model.eval()  # 设置为评估模式

    # 读取输入图像
    image_path = 'input_image.jpg'  # 替换为你的输入图像路径
    image = Image.open(image_path).convert('RGB')

    # 对图像进行预处理
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # 使用 ImageNet 的标准化
    ])
    image_tensor = transform(image).unsqueeze(0)  # 添加 batch 维度

    # 进行推断
    with torch.no_grad():
        output = model(image_tensor.to('cuda:0'))

    # 获取 alpha mask（透明度图）
    alpha_mask = output['alpha'].detach().cpu().numpy().squeeze()  # 提取 alpha 通道
    alpha_mask = np.clip(alpha_mask, 0, 1)  # 确保 alpha 值在 [0, 1] 范围内

    # 将 alpha mask 应用于输入图像，提取前景
    foreground = np.array(image) * alpha_mask[..., None]  # 按照 alpha 值提取前景
    foreground = foreground.astype(np.uint8)

    J.plots([img, foreground])


main()
