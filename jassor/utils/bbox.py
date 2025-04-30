from typing import Union
import numpy as np
import torch


class BBox:
    XYWH = 'cxcywh'
    LURD = 'lurd'
    LUWH = 'luwh'

    def __init__(self, bbox: Union[list, np.ndarray, torch.Tensor], box_format: str = LURD):
        # bbox = array: [(a, b, c, d)]
        # abcd 的含义与 format 有关
        self._bbox = np.asarray(bbox, dtype=np.float32)
        self._box_format = box_format

    @property
    def bbox(self):
        return self._bbox

    @property
    def contour(self):
        return bbox_to_contour(self._bbox)

    def join_region(self, l, u, r, d, eps=5):
        bbox = self.lurd()
        bbox, ps = bbox_join_region(bbox, l, u, r, d, eps)
        return BBox(bbox, self.LURD), ps

    def area(self):
        bbox = self.xywh()
        return bbox._bbox[2] * bbox._bbox[3]

    def inter(self, bbox):
        assert isinstance(bbox, BBox), 'Type BBox is Necessary'
        bbox1 = self.xywh()._bbox
        bbox2 = bbox.xywh()._bbox
        inter_box, select_1, select_2 = bbox_inter(bbox1, bbox2)
        return BBox(inter_box, self.LURD), select_1, select_2

    def xywh(self):
        if self._box_format == self.XYWH:
            return self
        elif self._box_format == self.LUWH:
            bbox = bbox_luwh2xywh(self._bbox)
            return BBox(bbox, self.XYWH)
        elif self._box_format == self.LURD:
            bbox = bbox_lurd2xywh(self._bbox)
            return BBox(bbox, self.XYWH)
        else:
            raise TypeError('bbox format not implemented')

    def lurd(self):
        if self._box_format == self.LURD:
            return self
        elif self._box_format == self.XYWH:
            bbox = bbox_xywh2lurd(self._bbox)
            return BBox(bbox, self.LURD)
        elif self._box_format == self.LUWH:
            bbox = bbox_luwh2lurd(self._bbox)
            return BBox(bbox, self.LURD)
        else:
            raise TypeError('bbox format not implemented')

    def luwh(self):
        if self._box_format == self.LUWH:
            return self
        elif self._box_format == self.XYWH:
            bbox = bbox_xywh2luwh(self._bbox)
            return BBox(bbox, self.LUWH)
        elif self._box_format == self.LURD:
            bbox = bbox_lurd2luwh(self._bbox)
            return BBox(bbox, self.LUWH)
        else:
            raise TypeError('bbox format not implemented')


def bbox_to_contour(bbox: np.ndarray):
    # 使用 lurd 格式
    l, u, r, d = bbox.T
    contour = [[l, u], [r, u], [r, d], [l, d], [l, u]]
    contour = np.asarray(contour).transpose((2, 0, 1))
    return contour


def bbox_join_region(bbox: np.ndarray, l, u, r, d, eps):
    # join_region 使用 lurd 格式
    bbox = bbox.copy()
    bbox[bbox[:, 0] >= r - eps, 0] = np.nan  # bbox at box right
    bbox[bbox[:, 1] >= d - eps, 1] = np.nan  # bbox at box down
    bbox[bbox[:, 2] <= l + eps, 2] = np.nan  # bbox at box left
    bbox[bbox[:, 3] <= u + eps, 3] = np.nan  # bbox at box up
    ps = ~np.isnan(bbox.sum(axis=0))
    bbox = bbox[ps, :]
    ps = ps.nonzero()

    # limit to box
    bbox[bbox[:, 0] < l, 0] = l
    bbox[bbox[:, 1] < u, 1] = u
    bbox[bbox[:, 2] > r, 2] = r
    bbox[bbox[:, 3] > d, 3] = d

    # [l, u, r, d]
    return bbox, ps


def bbox_inter(bbox1: np.ndarray, bbox2: np.ndarray):
    # inter 先使用 xywh 格式，再使用 lurd 格式，返回的是 lurd 格式
    # 计算相交面积，面积非零的索引拎出来
    area_matrix = bbox_inter_area_matrix(bbox1, bbox2)
    i, j = area_matrix.nonzero()
    # 按索引拎出来之后，轮廓之间就对齐了
    bbox1 = bbox1[i, :]
    bbox2 = bbox2[j, :]
    # 转换格式
    bbox1 = bbox_xywh2lurd(bbox1)
    bbox2 = bbox_xywh2lurd(bbox2)
    # 然后按照对齐的结果计算轮廓匹配结果
    l1, u1, r1, d1 = bbox1.T
    l2, u2, r2, d2 = bbox2.T
    l, u, r, d = np.maximum(l1, l2), np.maximum(u1, u2), np.minimum(r1, r2), np.minimum(d1, d2)
    return np.stack([l, u, r, d], axis=1), i, j


def bbox_inter_area_matrix(bbox1: np.ndarray, bbox2: np.ndarray) -> np.ndarray:
    # inter 使用 xywh 格式
    # 逻辑：对于 bbox1[i] 和 bbox2[j]，做如下计算：
    # if abs(xi - xj) * 2 >= (wi + wj): continue
    # if abs(yi - yj) * 2 >= (hi + hj): continue
    # 我要计算的不是两个轮廓的面积交并比，而是上级轮廓占下级的比例
    # x 方向上相交区域为 min(max(0, wi+wj-abs(xi-xj)), min(2*wi, 2*wj))，y 方向同理
    # inter = min((wi + wj) / 2 - abs(xi - xj), wi, wj) * min((hi + hj) / 2 - abs(yi - yj), hi, hj)
    # 然后把这个逻辑直接放到 numpy 上加速计算
    # 按列拆分
    x1, y1, w1, h1 = bbox1.T
    x2, y2, w2, h2 = bbox2.T
    # 计算中间矩阵（1 在 行，2 在 列）
    x_sub = abs(x1[:, None] - x2[None, :])
    y_sub = abs(y1[:, None] - y2[None, :])
    w_add = w1[:, None] + w2[None, :]
    h_add = h1[:, None] + h2[None, :]
    disjoint = (x_sub * 2 > w_add) | (y_sub * 2 > h_add)
    inter_w = w_add / 2 - x_sub
    inter_w = np.minimum(inter_w, w1[:, None])
    inter_w = np.minimum(inter_w, w2[None, :])
    inter_h = h_add / 2 - x_sub
    inter_h = np.minimum(inter_h, h1[:, None])
    inter_h = np.minimum(inter_h, h2[None, :])
    inter_area = (~disjoint) * inter_w * inter_h
    return inter_area


def bbox_lurd2xywh(bbox: np.ndarray) -> np.ndarray:
    bbox = bbox.copy()
    bbox[:, (2, 3)] = bbox[:, (2, 3)] - bbox[:, (0, 1)]
    bbox[:, (0, 1)] = bbox[:, (0, 1)] + bbox[:, (2, 3)] / 2
    return bbox


def bbox_xywh2lurd(bbox: np.ndarray) -> np.ndarray:
    bbox = bbox.copy()
    bbox[:, (0, 1)] = bbox[:, (0, 1)] - bbox[:, (2, 3)] / 2
    bbox[:, (2, 3)] = bbox[:, (0, 1)] + bbox[:, (2, 3)]
    return bbox


def bbox_luwh2xywh(bbox: np.ndarray) -> np.ndarray:
    bbox = bbox.copy()
    bbox[:, (0, 1)] = bbox[:, (0, 1)] + bbox[:, (2, 3)] / 2
    return bbox


def bbox_xywh2luwh(bbox: np.ndarray) -> np.ndarray:
    bbox = bbox.copy()
    bbox[:, (0, 1)] = bbox[:, (0, 1)] - bbox[:, (2, 3)] / 2
    return bbox


def bbox_lurd2luwh(bbox: np.ndarray) -> np.ndarray:
    bbox = bbox.copy()
    bbox[:, (2, 3)] = bbox[:, (2, 3)] - bbox[:, (0, 1)]
    return bbox


def bbox_luwh2lurd(bbox: np.ndarray) -> np.ndarray:
    bbox = bbox.copy()
    bbox[:, (2, 3)] = bbox[:, (0, 1)] + bbox[:, (2, 3)]
    return bbox
