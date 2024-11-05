import numpy as np
import matplotlib.pyplot as plt
import jassor.utils as J


def main():
    print('第一段程序描述图像任务中最常见的半步长融合方法')
    demo1()
    input('输入任意字符以继续...')
    print('第二段程序描述一维数据类型的融合方法')
    demo2()
    input('输入任意字符以继续...')
    print('第三段程序描述一般性的接口用法')
    demo3()


def demo1():
    # 四张图块
    x1 = np.zeros((100, 100, 3)) + [255, 0, 0]
    x2 = np.zeros((100, 100, 3)) + [0, 255, 0]
    x3 = np.zeros((100, 100, 3)) + [0, 255, 255]
    x4 = np.zeros((100, 100, 3)) + [0, 0, 255]
    xs = [x1, x2, x3, x4]
    # 对应坐标（左上、右上、左下、右下）
    # None 表示该维度广播或全写，不需要给出具体坐标
    g1 = (0, 0, None)
    g2 = (0, 50, None)
    g3 = (50, 0, None)
    g4 = (50, 50, None)
    gs = [g1, g2, g3, g4]

    # 创建融合器并融合
    for index, steep in enumerate([1, 2, 3, 4]):
        # 对图片来说，高斯模糊只应用在
        merger = J.Merger(temp=(150, 150, 3), kernel=(100, 100, 1), dtype=np.float32, steep=steep)
        for x, g in zip(xs, gs):
            merger.set(x, g)
        result = merger.tail().round().astype(np.uint8)
        plt.subplot(2, 2, index + 1)
        plt.imshow(result)
    # steep 越大，中心权重越高，融合结果越倾向于“划界而治”
    # steep 越小，中心权重与边缘权重越接近，融合结果越倾向于“简单叠加”
    plt.show()


def demo2():
    # 两条输入
    x1 = np.zeros((6,), dtype=np.float16) + 0
    x2 = np.zeros((6,), dtype=np.float16) + 1
    # 对应坐标
    g1 = (0,)
    g2 = (3,)
    # float16 只能支撑到 1e-7 的精度
    merger = J.Merger(temp=(10,), kernel=(6,), dtype=np.float16, eps=1e-7)
    merger.set(x1, g1)
    merger.set(x2, g2)
    result = merger.tail()
    # ≈ [0.     0.     0.     0.2     0.5    0.8     1.     1.     1.     0.    ]
    print(result)


def demo3():
    # temp.shape.length == kernel.shape.length
    # kernel 为 1 的维度，融合时应用广播机制，在该维度上不受高斯核影响
    # 一般的，kernel 至少应当在某一个维度非 1，否则高斯核将完全失去作用
    merger = J.Merger(temp=(2, 3, 4, 5, 6, 7, 8), kernel=(1, 1, 1, 3, 1, 1, 1))
    # 贴片时，patch 与 temp 长度一致的维度数，grid 坐标置 None 即可
    # 在 kernel 长度非 1 的维度数上，patch 的长度必须与 kernel 保持一致
    merger.set(patch=np.zeros((2, 3, 1, 3, 1, 2, 3)), grid=(None, None, 0, 1, 2, 3, 4))
    merger.set(patch=np.zeros((1, 1, 1, 3, 4, 3, 2)), grid=(0, 0, 0, 2, 0, 0, 0))
    # 允许对越界坐标执行贴片操作，当然，这不会有任何实际效果，仅作为一种容错
    merger.set(patch=np.zeros((3, 3, 3, 3, 3, 3, 3)), grid=(10, 10, 10, 10, 10, 10, 10))
    # 也允许对跨界坐标执行贴片操作，这将使 patch 中的一小部分作用于 temp 上
    # 但是请注意，负数坐标在这里并不表达“倒数”的含义
    merger.set(patch=np.zeros((1, 1, 1, 3, 1, 1, 1)), grid=(0, 0, 0, -1, 0, 0, 0))
    merger.set(patch=np.zeros((1, 1, 1, 3, 1, 1, 1)), grid=(0, 0, 0, 4, 0, 0, 0))
    # tail 将返回融合后的结果，这个结果会通过计算消除高斯核乘积的影响
    # 但建议不要将融合结果当精确值看待，融合结果只适合用于执行 argmax、 <= 等操作
    result = merger.tail()
    print(result.shape)


if __name__ == '__main__':
    main()
