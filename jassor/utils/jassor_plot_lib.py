import matplotlib
import torch

matplotlib.use('TkAgg')  # 好像只有这个支持
import math
from typing import List, Any, Tuple
from PIL import Image
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import importlib.util
import cv2
import numpy as np

shapely_ok = importlib.util.find_spec('shapely') is not None
if shapely_ok:
    import shapely
    from shapely.geometry.base import BaseGeometry


def plot(item: Any, title: str = None, window_name: str = 'jassor_plot', save_to: str = None, dpi: int = 1000, ticks: bool = False):
    title = title or ''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    _plot_item(ax, item)
    ax.set_title(str(title))
    ax.set_aspect('equal')
    if not ticks:
        # ax.axis('off')
        ax.set_xticks([])
        ax.set_yticks([])

    fig.canvas.manager.set_window_title(window_name)
    plt.tight_layout()
    if not save_to:
        plt.show(block=True)
    else:
        plt.savefig(save_to, dpi=dpi)
    plt.close(fig=fig)


def plots(items: List[Any], titles: List[str] = None, window_name: str = 'jassor_plot', save_to: str = None, dpi: int = 1000, ticks: bool = False):
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
        if not ticks:
            # ax.axis('off')
            ax.set_xticks([])
            ax.set_yticks([])

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

    if isinstance(item, torch.Tensor):
        item = item.detach().cpu().numpy()

    if isinstance(item, np.ndarray):
        # ndarray 必须是 (h, w, (1, 3, 4)) 或 (h, w)
        if len(item.shape) not in (2, 3) or min(item.shape) == 0:
            return ax.imshow(_draw_empty(f'only (h, w, c) or (h, w) are supported, got {item.shape}'))
        if len(item.shape) == 3 and item.shape[2] not in (1, 3, 4):

            return ax.imshow(_draw_empty(f'allowed color-type in GRAY, RGB, RGBA, got {item.shape}'))
        # return ax.imshow(Image.fromarray(item))
        return ax.imshow(item)

    if not bool(item):
        return ax.imshow(_draw_empty(f'item:{item}'))

    if isinstance(item, str):
        return ax.imshow(Image.open(item))

    if isinstance(item, Image.Image):
        return ax.imshow(item)

    if isinstance(item, List):
        # 点列类
        shape = []
        it = item
        while it and isinstance(it, (List, Tuple)) and len(it)>0:
            shape.append(len(it))
            it = it[0]
            if isinstance(it, np.ndarray):
                shape += it.shape
                break
        # [contour]
        if len(shape) not in (2, 3):
            return ax.imshow(_draw_empty(f'Only support contour or contours shape (c, n, 2) or (c, 2, n), got shape=={shape}'))

        try:
            if len(shape) == 2:
                item = [item]
            for contour in item:
                # [(x, y)]
                if len(contour) > 2 and len(contour[0]) == 2:
                    xs, ys = zip(*contour)
                    ax.plot(xs, ys)
                    continue
                # [xs, ys]
                if len(contour) == 2 and len(contour[0]) > 2:
                    xs, ys = contour
                    ax.plot(xs, ys)
                    continue
                ax.clear()
                return ax.imshow(_draw_empty(f'Only support contour shape (n, 2) or (2, n), got {len(contour), len(contour[0])}'))
            return
        except BaseException as e:
            ax.clear()
            return ax.imshow(_draw_empty(f'Exception while transing coords, see: {e}'))

    if hasattr(item, 'geo'):
        item = item.geo

    if shapely_ok and isinstance(item, BaseGeometry):
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
