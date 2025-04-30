import numpy as np
import jassor.utils as J
import jassor.shape as S


def main():
    demo1()


def demo1():
    n = 100
    m = 80
    bbox1 = create_bbox(n, -100, 100, 3, 7)
    bbox2 = create_bbox(m, -100, 100, 3, 7)
    bbox_inter, i, j = bbox1.inter(bbox2)
    shape1 = convert_bbox_shape(bbox1.lurd().bbox)
    shape2 = convert_bbox_shape(bbox2.lurd().bbox)
    shape = convert_bbox_shape(bbox_inter.lurd().bbox)
    shape1s = convert_bbox_shape(bbox1.lurd().bbox[i])
    shape2s = convert_bbox_shape(bbox2.lurd().bbox[j])
    J.plots([shape1, shape2, shape, shape1s, shape2s])


def convert_bbox_shape(bbox: np.ndarray) -> S.Shape:
    shape = [S.Region(l, u, r, d) for l, u, r, d in bbox]
    shape = S.MultiComplexPolygon(shapes=shape)
    return shape


def create_bbox(num, range_min, range_max, size_min, size_max):
    x = np.random.random(num) * (range_max - range_min) + range_min
    y = np.random.random(num) * (range_max - range_min) + range_min
    w = np.random.random(num) * (size_max - size_min) + size_min
    h = np.random.random(num) * (size_max - size_min) + size_min
    bbox = np.array([x, y, w, h]).T
    bbox = J.BBox(bbox, box_format=J.BBox.XYWH)
    return bbox


if __name__ == '__main__':
    main()
