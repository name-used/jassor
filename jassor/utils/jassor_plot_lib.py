import math
from typing import List, Any, Iterable, Tuple
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
    _plot_item(ax, item)
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
    for ax in axs[n:]:
        fig.delaxes(ax)

    for ax, item, title in zip(axs, items, titles):
        _plot_item(ax, item)
        ax.set_title(str(title))
        ax.set_aspect('equal')

    fig.canvas.manager.set_window_title(window_name)
    plt.tight_layout()
    if not save_to:
        plt.show(block=True)
    else:
        plt.savefig(save_to, dpi=dpi)
    plt.close(fig=fig)


def _plot_item(ax: Axes, item: Any) -> Any:

    # 支持三大类显示方式：
    # 图像显示：np.array, torch.Tensor, PIL.Image, str（file_path）
    # 点列显示：[[(x1, y1), (x2, y2), ...]], [[x1, x2, ...], [y1, y2, ...]]
    # 轮廓显示：shapely.geometry

    if item is None:
        return ax.imshow(_draw_empty(f'item is None'))

    if isinstance(item, np.ndarray):
        # ndarray 必须是 (h, w, (1, 3, 4)) 或 (h, w)
        if len(item.shape) not in (2, 3) or min(item.shape) == 0:
            return ax.imshow(_draw_empty(f'only (h, w, c) or (h, w) are supported, got {item.shape}'))
        if len(item.shape) == 3:
            return ax.imshow(_draw_empty(f'allowed color-type in GRAY, RGB, RGBA, got {item.shape}'))
        return ax.imshow(Image.fromarray(item))

    if not bool(item):
        return ax.imshow(_draw_empty(f'item:{item}'))

    if isinstance(item, str):
        return ax.imshow(Image.open(item))

    if isinstance(item, Image.Image):
        return ax.imshow(item)

    if isinstance(item, List):
        # 点列类
        if len(item) > 2 and len(item[0]) == 2:
            # [(x, y)]
            xs, ys = zip(*item)
            return ax.plot(xs, ys)
        if len(item) == 2 and len(item[0]) > 2:
            # [xs, ys]
            xs, ys = item
            return ax.plot(xs, ys)
        shape = []
        while item and isinstance(item, (List, Tuple)) and len(item)>0:
            shape.append(len(item))
            item = item[0]
        return ax.imshow(_draw_empty(f'Only support formats like [(x, y)] or [xs, ys], must num > 2, got shape=={shape}'))

    if hasattr(item, 'geo'):
        item = item.geo

    if isinstance(item, BaseGeometry):
        l, u, r, d = list(map(float, item.bounds))
        ax.set_xticks([l, r])
        ax.set_yticks([u, d])
        m = max(l, u, r, d) * 0.05
        ax.set_xlim(l - m, r + m)
        ax.set_ylim(u - m, d + m)
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
                continue
            if isinstance(geo, (shapely.LineString, shapely.LinearRing)):
                xs, ys = geo.xy
                ax.plot(xs, ys)
                continue
            if isinstance(geo, shapely.Polygon):
                xs, ys = geo.exterior.xy
                ax.fill(xs, ys, color='blue', alpha=0.5)
                for interior in geo.interiors:
                    xs, ys = interior.xy
                    ax.fill(xs, ys, color='white', alpha=1)
                ax.set_aspect('equal')
                # ax.set_title('Polygon with Hole')
                # ax.legend()
                continue
            # 存在不兼容类型，直接清空之前画的东西
            ax.clear()
            return ax.imshow(_draw_empty(f'Support shapely type Point、LineString、LineRing、Polygon. Unknown with in-type: {type(geo)} -- {geo}'))
        return  # 显示 shapely
    return ax.imshow(_draw_empty(f'Unknown type: {type(item)} -- {item}'))


def _draw_empty(message: str) -> Image.Image:
    # 最大保留两百个字符，再多没意义
    message = message[:200]
    lines = [message[p * 30: (p + 1) * 30] for p in range(math.ceil(len(message) / 30))]
    temp = np.zeros((20 + 30 * len(lines), 20 + 19 * min(len(message), 30), 3), dtype=np.uint8)
    for p, txt in enumerate(lines):
        cv2.putText(temp, txt, (10, 10 + 30 * (p + 1)), cv2.FONT_HERSHEY_SIMPLEX, 1, [180, 255, 60])
    return Image.fromarray(temp)
