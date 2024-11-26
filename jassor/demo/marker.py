import cv2
import numpy as np
import albumentations as A
import jassor.utils as J
from jassor.components import Marker


def main():
    print('第一段程序描述基本用法')
    demo1()
    input('输入任意字符以继续...')
    print('第二段程序测试破坏抗性')
    demo2()


def demo1():
    w = h = 768
    image = J.random_rainbow_curves((h, w, 3), s=67)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    # 变换至目标域
    temp = Marker.map_to(image)
    # 在目标域写入信息，目标域为 8*8 dct 矩阵，可以在每个小矩阵的第 7*7 个位置写入频域信息
    convas = np.zeros((h // Marker.k, w // Marker.k), dtype=np.uint8)
    cv2.putText(convas, 'hello', (3, 20), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=1, thickness=1)
    cv2.putText(convas, 'world', (3, 40), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=1, thickness=1)
    cv2.putText(convas, 'jassor', (3, 60), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=1, thickness=1)
    temp[7::8, 7::8] += convas
    # 变回去
    result = Marker.imap_to(temp)
    # 可以再提取信息
    mark = Marker.map_to(result)

    # 显示标签
    temp = temp[7::8, 7::8]
    temp = np.log(abs(temp) + 1) * np.sign(temp)
    mark = mark[7::8, 7::8]
    mark = np.log(abs(mark) + 1) * np.sign(mark)
    J.plots([image, result, temp, mark])


def demo2():
    image = cv2.imread(rf'../../resources/test.jpg', flags=cv2.IMREAD_GRAYSCALE)
    h, w = image.shape
    # 变换至目标域
    temp = Marker.map_to(image)
    # 在目标域写入信息，目标域为 8*8 dct 矩阵，可以在每个小矩阵的第 7*7 个位置写入频域信息
    convas = np.zeros((h // Marker.k, w // Marker.k), dtype=np.uint8)
    cv2.putText(convas, 'jassor', (20, 80), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=2, color=1, thickness=3)
    temp[7::8, 7::8] += convas
    # 变回去
    result = Marker.imap_to(temp)

    # 破坏结果后观察信息是否湮灭
    # 此方案对颜色调节不敏感，对平移抗性较强，对旋转缩放抗性较差
    # 在保持对原图影响较低的前提下，相对隐写而言，该水印不易灭失
    # 但对方只需同样应用 idct 变换后消灭频域信息即可破坏该水印，该盲水印写法不存在加密防护
    result = A.Compose([
        A.RandomGamma(p=1),
        # A.RandomRain(p=1),
        A.RandomBrightnessContrast(p=1),
    ])(image=np.stack([result, result, result], axis=2))['image'][:, :, 0]
    M = get_affine()
    result = cv2.warpAffine(result, M, (result.shape[1], result.shape[0]))

    # 再提取信息
    mark = Marker.map_to(result)

    # 显示标签
    temp = temp[7::8, 7::8]
    temp = np.log(abs(temp) + 1).clip(0, 1) * np.sign(temp)
    mark = mark[7::8, 7::8]
    mark = np.log(abs(mark) + 1).clip(0, 1) * np.sign(mark)
    J.plots([image, result, temp, mark])


def get_affine():
    # 参数定义
    angle = 7  # 旋转角度（度数）
    scale = 1  # 缩放比例
    tx, ty = 0, 0  # 平移量
    center = (960, 540)  # 旋转中心
    M = cv2.getRotationMatrix2D(center, angle, scale)
    M[0, 2] += tx
    M[1, 2] += ty
    return M


if __name__ == '__main__':
    main()
