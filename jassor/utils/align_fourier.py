"""
Fourier-Mellin (frequency-domain) affine registration (rotation/scale/translation + optional reflection).

Conventions:
- dx, dy: pixel translation from image1 to image2 AFTER (optional reflection) + rotation/scale about image center.
         dx > 0 means move right, dy > 0 means move down.
- degree: counter-clockwise rotation from image1 to image2 (after optional reflection).
- scale: isotropic scale from image1 to image2 (after optional reflection).
- reflect: if True, we assume a LEFT-RIGHT mirror (flip around vertical axis) happened first.

Dependencies: numpy, opencv-python
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional, Union
import cv2
import numpy as np


@dataclass(frozen=True)
class AffineParams:
    dx: float
    dy: float
    degree: float  # CCW
    scale: float
    reflect: bool  # left-right flip


def align_fourier(
    image1: np.ndarray,
    image2: np.ndarray,
    *,
    allow_reflect: bool = True,
    angle_bins: int = 720,
    radius_bins: int = 256,
    eps: float = 1e-6,
    return_matrix: bool = False,
) -> Union[Tuple[float, float, float, float, bool], np.ndarray]:
    """
    Main API:
        return_matrix == False -> return dx, dy, degree, scale, reflect (from image1 to image2)
        return_matrix == True -> return WarpAffineMatrix (from image1 to image2)
    Notes:
    - Works best when the "core content" stays in-frame and borders are 0 (as you described).
    - If allow_reflect=True, we test reflect=False vs reflect=True (left-right flip) and pick the better one.
    """
    img1 = _to_gray_f32(image1)
    img2 = _to_gray_f32(image2)
    img1, img2 = _pad_to_same_shape(img1, img2)

    candidates = [False, True] if allow_reflect else [False]

    best: Optional[Tuple[float, AffineParams]] = None  # (score, params)
    for reflect in candidates:
        base1 = cv2.flip(img1, 1) if reflect else img1
        dx, dy, deg, sc, score = _estimate_no_reflect(
            base1, img2,
            angle_bins=angle_bins,
            radius_bins=radius_bins,
            eps=eps,
        )
        params = AffineParams(dx=dx, dy=dy, degree=deg, scale=sc, reflect=reflect)
        if best is None or score > best[0]:
            best = (score, params)

    assert best is not None
    params = best[1]
    if return_matrix:
        # Matrix is defined on the internally padded coordinate frame.
        h, w = img2.shape
        return affine_matrix_from_params(params, (h, w))
    return params.dx, params.dy, params.degree, params.scale, params.reflect


def affine_matrix_from_params(params: AffineParams, shape_hw: Tuple[int, int]) -> np.ndarray:
    """
    Convenience: build a 2x3 affine matrix that maps image1 -> image2.

    If params.reflect=True, this matrix includes a left-right flip around the image center.
    """
    h, w = shape_hw
    cx, cy = w / 2.0, h / 2.0

    # Rotation+scale around center
    M = cv2.getRotationMatrix2D((cx, cy), params.degree, params.scale).astype(np.float32)

    # Add translation
    M[0, 2] += params.dx
    M[1, 2] += params.dy

    if not params.reflect:
        return M

    # Left-right reflection around center as an affine matrix:
    # x' = -x + 2*cx, y' = y
    R = np.array([[-1, 0, 2 * cx],
                  [ 0, 1,      0]], dtype=np.float32)

    # Total = M ∘ R  (first reflect, then rotate/scale/translate)
    # Compose 2x3 matrices via homogeneous 3x3
    Mh = _to_homo(M)
    Rh = _to_homo(R)
    Th = Mh @ Rh
    return Th[:2, :]


# ----------------- internals -----------------

def _estimate_no_reflect(
    img1: np.ndarray,
    img2: np.ndarray,
    *,
    angle_bins: int,
    radius_bins: int,
    eps: float,
) -> Tuple[float, float, float, float, float]:
    """
    Returns: dx, dy, degree, scale, score
    """
    # --- rotation + scale by Fourier-Mellin (log-polar magnitude phase correlation)
    rs = _estimate_rot_scale(img1, img2, angle_bins=angle_bins, radius_bins=radius_bins, eps=eps)

    # Rotation ambiguity: magnitude spectrum is (near) 180°-ambiguous in practice.
    deg0, sc0 = rs.degree, rs.scale
    deg_candidates = [deg0, _wrap_deg(deg0 + 180.0)]

    # --- pick the best (degree, translation) combo by direct similarity score
    h, w = img1.shape
    center = (w / 2.0, h / 2.0)

    best = None  # (score, dx, dy, deg, sc)
    for deg in deg_candidates:
        M = cv2.getRotationMatrix2D(center, deg, sc0).astype(np.float32)
        img1_rs = cv2.warpAffine(img1, M, (w, h), flags=cv2.INTER_LINEAR, borderValue=0)

        (dx, dy), _resp = cv2.phaseCorrelate(_win(img1_rs), _win(img2))

        score = _score_alignment(img1_rs, img2, dx, dy, eps=eps)
        if best is None or score > best[0]:
            best = (score, dx, dy, deg, sc0)

    assert best is not None
    score, dx, dy, deg, sc = best
    return dx, dy, deg, sc, score


@dataclass(frozen=True)
class _RotScale:
    degree: float
    scale: float


def _estimate_rot_scale(
    img1: np.ndarray,
    img2: np.ndarray,
    *,
    angle_bins: int,
    radius_bins: int,
    eps: float,
) -> _RotScale:
    h, w = img1.shape
    center = (w / 2.0, h / 2.0)
    max_r = min(center)

    mag1 = _log_mag(_win(img1))
    mag2 = _log_mag(_win(img2))

    # IMPORTANT: in cv2.warpPolar, dsize=(width, height) => output shape (height, width)
    # For WARP_POLAR_LOG, output rows ~ angle, cols ~ log-radius.
    lp1 = cv2.warpPolar(
        mag1, (radius_bins, angle_bins), center, max_r,
        flags=cv2.WARP_POLAR_LOG | cv2.INTER_LINEAR | cv2.WARP_FILL_OUTLIERS,
    )
    lp2 = cv2.warpPolar(
        mag2, (radius_bins, angle_bins), center, max_r,
        flags=cv2.WARP_POLAR_LOG | cv2.INTER_LINEAR | cv2.WARP_FILL_OUTLIERS,
    )

    (shift_x, shift_y), _ = cv2.phaseCorrelate(_win(lp1), _win(lp2))
    # shift_x: along cols => log-radius shift
    # shift_y: along rows => angle shift

    degree = -shift_y * 360.0 / float(angle_bins)
    degree = _wrap_deg(degree)

    # OpenCV's log-polar mapping implies: shift_x ≈ (radius_bins / log(max_r)) * log(1/scale)
    scale = float(np.exp(-shift_x * np.log(max_r + eps) / float(radius_bins)))

    return _RotScale(degree=degree, scale=scale)


def _to_gray_f32(img: np.ndarray) -> np.ndarray:
    if img.ndim == 3 and img.shape[-1] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = img.astype(np.float32, copy=False)
    return img


def _pad_to_same_shape(a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    ha, wa = a.shape
    hb, wb = b.shape
    h = max(ha, hb)
    w = max(wa, wb)

    def pad(x, th, tw):
        h0, w0 = x.shape
        top = (th - h0) // 2
        bottom = th - h0 - top
        left = (tw - w0) // 2
        right = tw - w0 - left
        if top == bottom == left == right == 0:
            return x
        return cv2.copyMakeBorder(x, top, bottom, left, right, borderType=cv2.BORDER_CONSTANT, value=0)

    return pad(a, h, w), pad(b, h, w)


def _win(img: np.ndarray) -> np.ndarray:
    """Hanning windowing + mean removal (helps phase correlation)."""
    img = img - float(img.mean())
    h, w = img.shape
    hann = cv2.createHanningWindow((w, h), cv2.CV_32F)
    return img * hann


def _log_mag(img: np.ndarray) -> np.ndarray:
    f = np.fft.fft2(img)
    f = np.fft.fftshift(f)
    mag = np.log1p(np.abs(f))
    mag = mag.astype(np.float32)
    # normalize for numerical stability
    mag = cv2.normalize(mag, None, 0, 1, cv2.NORM_MINMAX)
    return mag


def _score_alignment(img1_rs: np.ndarray, img2: np.ndarray, dx: float, dy: float, *, eps: float) -> float:
    h, w = img2.shape
    T = np.array([[1, 0, dx], [0, 1, dy]], dtype=np.float32)
    moved = cv2.warpAffine(img1_rs, T, (w, h), flags=cv2.INTER_LINEAR, borderValue=0)

    # score on overlap (non-zero-ish) area
    m = (np.abs(moved) > 1.0) & (np.abs(img2) > 1.0)
    if m.sum() < 64:
        # fallback: use whole image (still works if borders are mostly zero)
        m = np.ones_like(img2, dtype=bool)

    a = moved[m].astype(np.float32)
    b = img2[m].astype(np.float32)
    a = a - a.mean()
    b = b - b.mean()
    denom = (np.linalg.norm(a) * np.linalg.norm(b) + eps)
    return float(np.dot(a, b) / denom)


def _wrap_deg(deg: float) -> float:
    """Wrap to (-180, 180]."""
    return float((deg + 180.0) % 360.0 - 180.0)


def _to_homo(M2x3: np.ndarray) -> np.ndarray:
    M = np.eye(3, dtype=np.float32)
    M[:2, :] = M2x3.astype(np.float32)
    return M
