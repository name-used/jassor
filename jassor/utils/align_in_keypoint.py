from __future__ import annotations
from typing import Tuple, Optional, Union, Literal
import numpy as np
import cv2
import math


def align_keypoint(
    image1: np.ndarray,
    image2: np.ndarray,
    *,
    method: Literal["orb", "akaze", "sift"],
    allow_reflect: bool = True,
    max_features: int = 4000,
    ratio: float = 0.75,
    ransac_thresh: float = 3.0,
    confidence: float = 0.99,
    refine_iters: int = 20,
    return_matrix: bool = False,
) -> Union[Tuple[float, float, float, float, bool], np.ndarray]:
    """
    Feature/keypoint based registration.
    return_matrix == False -> (dx, dy, degree, scale, reflect)
    return_matrix == True  -> 2x3 affine matrix mapping image1 -> image2 (includes reflection if reflect=True)
    """

    img1 = _to_gray_u8(image1)
    img2 = _to_gray_u8(image2)

    best = None  # (score, M2x3, reflect)

    for reflect in ([False, True] if allow_reflect else [False]):
        base1 = cv2.flip(img1, 1) if reflect else img1

        kp1, des1 = _detect(method, base1, max_features)
        kp2, des2 = _detect(method, img2,  max_features)
        if des1 is None or des2 is None or len(kp1) < 6 or len(kp2) < 6:
            continue

        pts1, pts2 = _match_points(method, kp1, des1, kp2, des2, ratio=ratio)
        if pts1 is None or len(pts1) < 6:
            continue

        M, inliers = cv2.estimateAffinePartial2D(
            pts1, pts2,
            method=cv2.RANSAC,
            ransacReprojThreshold=ransac_thresh,
            confidence=confidence,
            refineIters=refine_iters,
        )
        if M is None:
            continue

        inlier_count = int(inliers.sum()) if inliers is not None else 0
        # 简单打分：inlier 越多越好；你也可以换成重投影误差
        score = inlier_count

        if best is None or score > best[0]:
            best = (score, M.astype(np.float32), reflect)

    if best is None:
        # 你可以选择 raise；或回退到 align_fourier
        raise RuntimeError("align_kp failed: not enough matches / cannot estimate affine.")

    _, M_est, reflect = best

    # 如果 reflect=True，M_est 是“flip(image1) -> image2”的矩阵
    # 但你接口希望“image1 -> image2”，并且 reflect 表示先做左右翻转
    # 所以 return_matrix 时需要把翻转也合进矩阵：  M_total = M_est ∘ Rflip
    if reflect:
        h, w = img1.shape[:2]
        cx = (w - 1) / 2.0
        Rflip = np.array([[-1, 0, 2 * cx],
                          [ 0, 1,      0]], dtype=np.float32)
        M_total = _compose_affine(M_est, Rflip)
    else:
        M_total = M_est

    if return_matrix:
        return M_total

    h, w = img1.shape[:2]
    cx = (w - 1) / 2.0
    cy = (h - 1) / 2.0
    dx, dy, degree, scale = _decompose_similarity(M_total, cx, cy)
    return dx, dy, degree, scale, reflect


# ---------------- helpers ----------------

def _to_gray_u8(img: np.ndarray) -> np.ndarray:
    if img.ndim == 3 and img.shape[-1] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if img.dtype != np.uint8:
        img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return img


def _detect(method: str, img: np.ndarray, max_features: int):
    if method == "orb":
        det = cv2.ORB_create(nfeatures=max_features, fastThreshold=7)
    elif method == "akaze":
        det = cv2.AKAZE_create()
    elif method == "sift":
        det = cv2.SIFT_create(nfeatures=max_features)
    else:
        raise ValueError(method)
    return det.detectAndCompute(img, None)


def _match_points(method: str, kp1, des1, kp2, des2, *, ratio: float):
    if method in ("orb", "akaze"):
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    else:  # sift
        matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)

    knn = matcher.knnMatch(des1, des2, k=2)
    good = []
    for m, n in knn:
        if m.distance < ratio * n.distance:
            good.append(m)

    if len(good) < 6:
        return None, None

    pts1 = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    pts2 = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    return pts1, pts2


def _compose_affine(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    # A ∘ B : 先做 B，再做 A
    Ah = np.eye(3, dtype=np.float32); Ah[:2, :] = A
    Bh = np.eye(3, dtype=np.float32); Bh[:2, :] = B
    Ch = Ah @ Bh
    return Ch[:2, :]


def _decompose_similarity(M: np.ndarray, cx: float, cy: float) -> Tuple[float, float, float, float]:
    # M = [[a,b,tx],[c,d,ty]]
    a, b, tx = float(M[0, 0]), float(M[0, 1]), float(M[0, 2])
    c, d, ty = float(M[1, 0]), float(M[1, 1]), float(M[1, 2])

    # 对“相似变换”来说：scale = sqrt(a^2 + c^2)  （第一列的长度）
    s1 = math.sqrt(a * a + c * c)  # 第一列长度
    s2 = math.sqrt(b * b + d * d)  # 第二列长度
    scale = (s1 + s2) * 0.5

    # 角度：atan2(c, a) 对应 CCW（在 OpenCV 图像坐标 y向下时，这个约定仍然可用作“warpAffine 的角度”）
    # degree = math.degrees(math.atan2(c, a))
    degree = math.degrees(math.atan2(b, a))  # 用 b,a
    # wrap 到 (-180,180]
    degree = (degree + 180.0) % 360.0 - 180.0

    dx = tx - ((1 - a) * cx - b * cy)
    dy = ty - (b * cx + (1 - a) * cy)

    return dx, dy, degree, scale
