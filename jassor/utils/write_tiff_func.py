from typing import Union
from pathlib import Path
import inspect
import math
import numpy as np
import tifffile
from skimage.transform import resize
import cv2


photometric_map = {
    # 来自 GPT
    'MINISWHITE': 0,  # 单通道图像中，0 表示白色，最大值表示黑色（老式习惯）
    'MINISBLACK': 1,  # 单通道图像中，0 表示黑色，最大值表示白色（现代标准）
    'RGB': 2,  # 多通道彩色图像，3 个通道分别表示 R、G、B
    'PALETTE': 3,  # 图像值为颜色查找表（colormap）中的索引
    'MASK': 4,  # 通常用于蒙版或 alpha
    'SEPARATED': 5,  # CMYK 色彩空间（青品黄黑）
    'YCBCR': 6,  # YCbCr 色彩空间（通常用于 JPEG 编码）
    'CIELAB': 8,  # Lab 色彩空间
    'CFA': 32803,  # Color Filter Array，传感器原始图像（如 Bayer 图）
    'LOGHUFFMAN': 32844,  # 用于 LogLuv 图像
    'LINEARRAW': 34892,  # 用于 Raw 图像数据
    # 在 tifffile 中还可能支持字符串形式，比如：'minisblack'、'rgb'、'palette'、'cfa' 等。
}
compression_map = {
    'NONE': 1,  # 单通道图像中，0 表示白色，最大值表示黑色（老式习惯）
    'LZW': 5,  # Lempel-Ziv-Welch 压缩
    'JPEG': 6,  # JPEG 压缩（通常与 YCbCr 配合）
    'JPEGOLD': 7,  # 老式 JPEG（不推荐）
    'ZLIB': 8,  # zlib 压缩
    'DEFLATE': 32946,  # ADOBE 定义的 deflate 算法
    'PACKBITS': 32773,  # 一种简单的 RLE 压缩
    'LERC': 34925,  # Limited Error Raster Compression，用于 GIS
    'ZSTD': 50001,  # Facebook 提出的压缩算法
    'LZMA': 50002,  # Lempel-Ziv-Markov 压缩
    'WEBP': 50003,  # 用于 Web 图像压缩
    'auto': 'auto',  # 自动选择（仅在某些 tifffile 函数中支持）
}
interpolation_map = {
    'NEAREST': 0,
    'BILINEAR': 1,
    'LINEAR': 1,
}


def image2slide(
        image: np.ndarray,
        output_path: str,
        mpp: float,
        *,
        mag: float = None,
        level_count: int = None,
        tile_size: int = 512,
        compression: str = 'LZW',
        photometric: str = None,
        name: str = None,
        format: str = None,
        interpolation: str = 'Nearest',
        resize_anti_aliasing: Union[None, bool] = None,
        **options: str
) -> None:

    H, W, channel = image.shape if len(image.shape) == 3 else (*image.shape, 0)
    level_count = level_count or round(math.log2(max(H, W, 1024) / 1024)) + 1
    name = name or Path(output_path).name
    mag = mag or round(10 / mpp)
    dtype = image.dtype
    shapes = [
        (H // 2 ** level, W // 2 ** level)
        if channel == 0 else
        (H // 2 ** level, W // 2 ** level, channel)
        for level in range(level_count)
    ]
    tile_shape = (tile_size, tile_size) if channel == 0 else (tile_size, tile_size, channel)
    resolutions = [(10000 / mpp / 2**level, 10000 / mpp / 2**level) for level in range(level_count)]
    photometric = photometric or guess_photometric_key_strict(image)
    photometric = photometric_map[photometric.upper()]
    compression = compression_map[compression.upper()]
    interpolation = interpolation_map[interpolation.upper()]
    format = format or Path(output_path).suffix
    if format == '.svs':
        desc = f"Aperio Image Library v12.0.16\n{W}x{H} ({tile_size}x{tile_size}) |AppMag = {mag}|MPP = {mpp}|Filename = {name}"
    else:
        desc = f'Generic pyramidal\n{W}x{H} ({tile_size}x{tile_size}) |AppMag = {mag}|MPP = {mpp}|Filename = {name}'

    _options = dict(
        subifds=0, dtype=dtype,
        photometric=photometric, compression=compression,
        planarconfig='CONTIG', metadata=None,
        resolutionunit='CENTIMETER',
        **options
    )
    thumb_w, thumb_h = W, H
    while max(thumb_w, thumb_h) > 2000:
        thumb_w, thumb_h = thumb_w // 2, thumb_h // 2
    thumb_options = dict(
        shape=(thumb_h, thumb_w, 3),
        photometric=photometric_map['RGB'],
        compression=compression_map['LZW'],
        planarconfig='CONTIG',
        metadata=None,
        dtype=np.uint8,
        resolution=(10000 / mpp * thumb_w / W, 10000 / mpp * thumb_h / H),
        resolutionunit='CENTIMETER',
        **options,
    )

    with tifffile.TiffWriter(output_path, bigtiff=True) as writer:
        # 检查参数是否符合匹配要求，不符合直接报错
        try:
            sig = inspect.signature(writer.write)
            sig.bind(data=None, shape=None, tile=None, description=None, **_options)  # 模拟 func(**options) 的参数匹配
        except TypeError as e:
            print(f"参数不匹配: {e}")
            raise e

        # 第 1 张，完整全图，带描述
        writer.write(data=image, shape=shapes[0], tile=tile_shape[:2], description=desc, resolution=resolutions[0], **_options)
        # 若 svs 格式，第 2 张为缩略图
        if format == '.svs':
            thumb = make_thumb(image, thumb_w, thumb_h)
            writer.write(data=thumb, **thumb_options)
        # 降分辨率tile图，从大到小
        for level in range(1, level_count):
            image = resize(image, shapes[level][:2], order=interpolation, anti_aliasing=resize_anti_aliasing, preserve_range=True).astype(dtype, copy=False)
            writer.write(data=image, shape=shapes[level], tile=tile_shape[:2], description='', resolution=resolutions[level], **_options)


def make_thumb(image: np.ndarray, thumb_w, thumb_h):
    if np.issubdtype(image.dtype, np.floating):
        image = (image.clip(0, 1) * 255).round().astype(np.uint8)
    image = image.astype(np.uint8)
    if image.ndim == 2:
        image = image[..., None]
    if image.shape[2] < 3:
        image = np.concatenate([image, np.repeat(image[..., [-1]], 3 - image.shape[2], 2)], 2)
    elif image.shape[2] > 3:
        image = image[..., :3]
    image = cv2.resize(image, (thumb_w, thumb_h))
    return image


def guess_photometric_key_strict(img: np.ndarray) -> str:
    """
    规则：
    - 只有 (uint8/uint16) + 3通道 才判为 RGB
    - 只有 (uint8/uint16) + 0/1通道 才判为灰度(MINISBLACK)
    - 其它任何情况：回退到最宽泛兜底（MINISBLACK）
      （意味着你不再关心 ASAPSlide 的兼容性，只求 TIFF 能装下）
    返回 photometric_map 的 key
    """
    a = np.asarray(img)

    # 只把 uint8/uint16 当作“标准视觉图像”
    is_std_vis = a.dtype in (np.uint8, np.uint16)

    # ---------- 灰度：2D 或 3D 且最后一维为 1 ----------
    if is_std_vis:
        if a.ndim == 2:
            return "MINISBLACK"
        if a.ndim == 3:
            c = a.shape[-1]
            if c == 1:
                return "MINISBLACK"
            if c == 3:
                return "RGB"
            # uint8/uint16 但通道不是 1/3：也算“非标准视觉格式”
            return "MINISBLACK"

    # ---------- 非标准视觉格式：统一兜底 ----------
    #（你说“任意类型、任意通道”，这里就不做花活了）
    return "MINISBLACK"
