import jassor.utils as J
import numpy as np
import cv2

width = 1920
height = 1080
n = 2
k = 2 ** n


def main():
    """
    全程在整数上计算
    首先用 hadamard 矩阵实现类似 dct 那样的局部能量化加窗
    然后在 block 的能量域 (0, 0) 和频率域 (-1, -1) 分别写入信息, 其中, 能量域的信息写在模数里
    这些信息共同构成一个盲水印
    """
    image = cv2.imread(rf'C:\Users\jizhe\Pictures\test.jpg', cv2.IMREAD_GRAYSCALE)
    image = image.astype(np.int32)
    H = hadamard(n)

    temp = np.zeros_like(image)
    for i in range(0, height - k + 1, k):
        for j in range(0, width - k + 1, k):
            temp[i: i + k, j: j + k] = H @ image[i: i+k, j: j+k] @ H.T

    # 4 倍缩放的标记图, 信息在 8 倍缩放下
    mark = create_mark()
    temp[0::k, 0::k] = temp[0::k, 0::k] - temp[0::k, 0::k] % 4 + mark
    # temp[3::k, 3::k] = 2

    result = np.zeros_like(temp)
    for i in range(0, height - k + 1, k):
        for j in range(0, width - k + 1, k):
            result[i: i + k, j: j + k] = H @ temp[i: i+k, j: j+k] @ H.T

    logo = np.zeros_like(result)
    for i in range(0, height - k + 1, k):
        for j in range(0, width - k + 1, k):
            logo[i: i + k, j: j + k] = H @ result[i: i+k, j: j+k] @ H.T

    logo1 = find_mark(logo[0::k, 0::k])
    logo2 = find_mark(logo[3::k, 3::k])
    J.plots([image, result, logo1, logo2])

    # result = H @ image.astype(int) @ H.T
    # result = image // 2 * 2 + mark
    # logo = find_mark(result)
    # jassor.utils.plots([image, result, mark, logo])


def find_mark(image: np.ndarray):
    a = image[0::2, 0::2] % 4
    b = image[1::2, 1::2] % 4
    c = image[0::2, 1::2] % 4
    d = image[1::2, 0::2] % 4
    return ((a+b) > (c+d)).astype(np.uint8)


def create_mark():
    temp = np.zeros((height // k, width // k), dtype=np.uint8)
    convas = np.zeros((height // k // 2, width // k // 2), dtype=np.uint8)
    cv2.putText(convas, 'hello', (10, 86), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=1, thickness=3)
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
