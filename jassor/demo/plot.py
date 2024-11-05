import traceback

import cv2
import numpy as np
import shapely
import shapely.affinity as A
from PIL import Image

import jassor.utils as J
import jassor.shape as S


def main():
    # print('第一段程序描述基本用法')
    # demo1()
    # input('输入任意字符以继续...')
    # print('第二段程序描述多类型支持')
    # demo2()
    # input('输入任意字符以继续...')
    print('第三段程序描述空值与异常问题')
    demo3()


def demo1():
    # 可以一键式的展示单张图片或者多张图片
    imgs = []
    for i in range(7):
        img = np.zeros((50, 100, 3), dtype=np.uint8)
        cv2.putText(img, str(i), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, [180, 255, 60])
        imgs.append(img)
    J.plot(imgs[0], window_name='single_image')
    J.plots(imgs, window_name='multi_images')


def demo2():
    # ndarray
    p1 = np.zeros((50, 150, 3), dtype=np.uint8)
    cv2.putText(p1, 'ndarray', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, [180, 255, 60])

    # PIL.Image
    p2 = np.zeros((50, 200, 3), dtype=np.uint8)
    cv2.putText(p2, 'PIL.Image', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, [180, 255, 60])
    p2 = Image.fromarray(p2)

    # coords
    p3 = [(1, 1), (3, 1), (2, 2)]
    p4 = [[1, 3, 2], [1, 1, 2]]

    J.plots([p1, p2, p3, p4], window_name='numpy,image,coords')

    # shapely
    s1 = shapely.Point((1, 1))
    s2 = shapely.LineString([(2, 2), (2, 3), (3, 3), (3, 4)])
    s3 = shapely.LinearRing([(12, 12), (12, 13), (13, 13)])
    s4 = shapely.Polygon([(100, 100), (200, 100), (200, 200), (100, 200)], [
        [(110, 110), (120, 110), (120, 120), (110, 120)],
        [(150, 150), (160, 150), (160, 160), (150, 160)],
    ])
    s5 = shapely.MultiPoint(points=[(1, 1), (2, 2), (3, 3)])
    s6 = shapely.MultiLineString(lines=[s2, s3])
    s7 = shapely.MultiPolygon(polygons=[s4, A.translate(s4, 120, 120)])
    s8 = shapely.GeometryCollection(geoms=[s1, s2, s3, s4])
    J.plots([s1, s2, s3, s4, s5, s6, s7, s8], window_name='shapely')

    # jassor.shape
    js1 = S.create_regular_polygon(8, len_side=1)
    js2 = S.create_triangle([3, None, 4], [None, None, 60])
    js3 = S.create_triangle([3, None, None], [90, None, 60])
    js4 = S.create_polygon(len_sides=[2, 1, 1, 1.414], degrees=[90, 90, 135, 45])
    js5 = S.create_polygon(len_sides=[2, 1, 1], degrees=[90, 90, 135], ring_close=False)
    js6 = S.create_sector(1, 1)
    J.plots([js1, js2, js3, js4, js5, js6], window_name='J.shape_1')


def demo3():
    """
    plot 工具的主要作用是在开发工作期间辅助显示，通常不会出现在真正运行的代码中
    因此 plot 工具的核心理念是使用起来一定要足够简洁
    如果动不动就报错，这对开发工作来说是一种灾难
    因此对于不能正常显示的元素，本工具会考虑将其直接以图像方式显示在展示框中，而非报错
    """

    # 空类型
    J.plots([0, [], (), None, S.EMPTY, S.FULL, shapely.Point(), shapely.LineString(), shapely.Polygon()])
    # numpy 错类型
    J.plots([
        np.zeros((), dtype=np.uint8),
        np.zeros((1,), dtype=np.uint8),
        np.zeros((1, 0), dtype=np.uint8),
        np.zeros((10, 10, 2), dtype=np.uint8),
    ])
    # coords 错类型
    J.plots([
        [[], []],
        [[1,], [1,]],   # 只显示点列，不显示孤立点，孤立点可以用 shapely.MultiPoints 显示
        [[1], [1], [1]],   # 只显示点列，不显示孤立点，孤立点可以用 shapely.MultiPoints 显示
        [(1, 2, 3), (1, 2, 3), (1, 2, 3)],   # 只显示点列，不显示孤立点，孤立点可以用 shapely.MultiPoints 显示
    ])


main()
