import math
from typing import List, Any
import shapely
from PIL import Image
import matplotlib
from matplotlib.axes import Axes
matplotlib.use('TkAgg')     # 好像只有这个支持
import matplotlib.pyplot as plt
import cv2
import numpy as np
from shapely.geometry.base import BaseGeometry


def plot(item: Any, title: str = None, window_name: str = 'jassor_plot', save_to: str = None, dpi: int = 1000):
    title = title or ''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plot_item(ax, item)
    ax.set_title(str(title))
    ax.set_aspect('equal')

    fig.canvas.manager.set_window_title(window_name)
    plt.tight_layout()
    if not save_to:
        plt.show()
    else:
        plt.savefig(save_to, dpi=dpi)
    plt.close(fig=fig)


def plots(items: List[Any], titles: List[str] = None, window_name: str = 'jassor_plot', save_to: str = None, dpi: int = 1000):
    n = len(items)
    titles = (titles or []) + [''] * n
    # 计算行列数量
    row = int(n ** 0.5)
    col = (n + row - 1) // row

    fig, axs = plt.subplots(row, col)
    axs = [axs] if row == col == 1 else axs.flatten()

    for ax, item, title in zip(axs, items, titles):
        plot_item(ax, item)
        ax.set_title(str(title))
        ax.set_aspect('equal')

    fig.canvas.manager.set_window_title(window_name)
    plt.tight_layout()
    if not save_to:
        plt.show()
    else:
        plt.savefig(save_to, dpi=dpi)
    plt.close(fig=fig)


def plot_item(ax: Axes, item: Any) -> None:

    # 支持三大类显示方式：
    # 图像显示：np.array, torch.Tensor, PIL.Image, str（file_path）
    # 点列显示：[[(x1, y1), (x2, y2), ...]], [[x1, x2, ...], [y1, y2, ...]]
    # 轮廓显示：shapely.geometry
    if not item:
        # 空的直接画成图片
        text = f'item:{item}'
        # print(text)
        texts = [text[p*30: (p+1)*30] for p in range(math.ceil(len(text) / 30))]
        temp = np.zeros((20 + 30 * len(texts), 20 + 19 * min(len(text), 30), 3), dtype=np.uint8)
        for p, txt in enumerate(texts):
            cv2.putText(temp, txt, (10, 10 + 30*(p+1)), cv2.FONT_HERSHEY_SIMPLEX, 1, [180, 255, 60])
        ax.imshow(Image.fromarray(temp))
    elif isinstance(item, (np.ndarray, str, Image.Image)):
        # 图像类做转换
        if isinstance(item, str):
            item = Image.open(item)
        elif isinstance(item, np.ndarray):
            item = Image.fromarray(item)
        ax.imshow(item)
    elif isinstance(item, List):
        # 点列类
        if len(item) > 2 and len(item[0]) == 2:
            # [(x, y)]
            xs, ys = zip(item)
            ax.plot(xs, ys)
        elif len(item) == 2 and len(item[0]) > 2:
            # [xs, ys]
            xs, ys = item
            ax.plot(xs, ys)
        else:
            raise TypeError('Only support formats like [(x, y)] or [xs, ys]')
    elif isinstance(item, BaseGeometry) or hasattr(item, 'geo') and isinstance(item.geo, BaseGeometry):
        item = item if isinstance(item, BaseGeometry) else item.geo
        l, u, r, d = list(map(int, item.bounds))
        ax.set_xticks([l, r])
        ax.set_yticks([u, d])
        # ax.get_xaxis().set_visible(False)
        # ax.get_yaxis().set_visible(False)
        # 变换矩阵: matrix = [xAx, xAy, yAx, yAy, xb, yb]
        # img = affine_transform(img, [1, 0, 0, -1, 0, d])

        # 适配多图形和单图形
        geos = item.geoms if hasattr(item, 'geoms') else [item]
        for geo in geos:
            # 这是 shapely 的全部类型
            # [
            #     "Point",
            #     "LineString",
            #     "Polygon",
            #     "MultiPoint",
            #     "MultiLineString",
            #     "MultiPolygon",
            #     "GeometryCollection",
            #     "LinearRing",
            # ]
            if isinstance(geo, shapely.Point):
                ax.scatter(geo.x, geo.y)
            elif isinstance(geo, (shapely.LineString, shapely.LinearRing)):
                xs, ys = geo.xy
                ax.plot(xs, ys)
            elif isinstance(geo, shapely.Polygon):
                xs, ys = geo.exterior.xy
                ax.fill(xs, ys, color='blue', alpha=0.5)
                for interior in geo.interiors:
                    xs, ys = interior.xy
                    ax.fill(xs, ys, color='white', alpha=1)
                ax.set_aspect('equal')
                ax.set_title('Polygon with Hole')
                # ax.legend()
            else:
                raise TypeError(f'Support shapely type Point、LineString、LineRing、Polygon. Unknown with in-type: {type(geo)} -- {geo}')
