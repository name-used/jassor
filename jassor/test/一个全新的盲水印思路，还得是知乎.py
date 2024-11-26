import jassor.utils
import numpy as np
import cv2

width = 1920
height = 1080


def main():
    """
    这次试试这么做：
    全程在整数上计算
    首先用 hadamard 矩阵提取频域信息
    然后在
    """

    image = cv2.imread(rf'C:\Users\jizhe\Pictures\test.jpg', cv2.IMREAD_GRAYSCALE)
    image = image.astype(np.int32) - 128
    for n in range(1, 3):
        temp = np.zeros_like(image)
        H = hadamard(n)
        k = 2 ** n
        for i in range(0, height - k + 1, k):
            for j in range(0, width - k + 1, k):
                temp[i: i + k, j: j + k] = H @ image[i: i+k, j: j+k] @ H.T
                temp[i+k-1, j+k-1] = 1
                temp[i: i + k, j: j + k] = H @ temp[i: i+k, j: j+k] @ H.T
        jassor.utils.plots([image, temp])

    # result = H @ image.astype(int) @ H.T
    # result = image // 2 * 2 + mark
    # logo = find_mark(result)
    # jassor.utils.plots([image, result, mark, logo])




def find_mark(image: np.ndarray):
    a = image[0::2, 0::2] % 2
    b = image[1::2, 1::2] % 2
    c = image[0::2, 1::2] % 2
    d = image[1::2, 0::2] % 2
    return ((a+b) > (c+d)).astype(np.uint8)


def create_mark():
    temp = np.zeros((height, width), dtype=np.uint8)
    convas = np.zeros((height // 2, width // 2), dtype=np.uint8)
    cv2.putText(convas, 'hello', (256, 256), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=1, thickness=3)
    # 左上右下编码
    temp[0::2, 0::2] = convas
    temp[1::2, 1::2] = convas
    temp[0::2, 1::2] = 1 - convas
    temp[1::2, 0::2] = 1 - convas
    return temp


def hadamard(n):
    """构造 2^n 阶的哈达玛矩阵"""
    if n == 0:
        return np.array([[1]], dtype=np.int32)
    else:
        H = hadamard(n - 1)
        return np.block([
            [H, H],
            [H, -H]
        ])


main()
