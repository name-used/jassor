import math
from typing import Union, List
import inspect
import cv2
from skimage.transform import resize
import os
import traceback
from pathlib import Path
import zstandard as zstd
import numpy as np
import tifffile
from .write_tiff_func import interpolation_map, compression_map, photometric_map


class SlideWriter:
    """
    svs格式定义，TIFF或BIGTIFF，不能使用subifds
    第1张，全分辨率tile图，需设定desc
    第2张，缩略图
    第3到第N-2张，降分辨率tile图，必须使用从大到小顺序
    第N-1张，label图，需设定标志(ReducedImage 1 (0x1))，需设定desc
    第N张，marco图，需设定标志 (ReducedImage 1 (0x1), Macro 8 (0x8))，需设定desc
    """

    def __init__(
            self,
            output_path: str,
            tile_size: int,
            dimensions: tuple,
            mpp: float,
            channel: int,
            dtype: type,
            photometric: str,
            *,
            mag: float = None,
            compression: str = 'LZW',
            level_count: int = None,
            name: str = None,
            format: str = None,
            # interpolation: int = cv2.INTER_NEAREST,
            interpolation: str = 'Nearest',
            resize_anti_aliasing: Union[None, bool] = None,
            default_value: Union[int, List[int]] = 0,
            **options: str
    ):
        self.output_path = output_path
        self.tile_size = tile_size
        self.W, self.H = dimensions
        # 要求横纵分辨率一致
        self.mpp = mpp
        self.mag = mag or round(10 / mpp)
        self.level_count = level_count or round(math.log2(max(self.H, self.W, 1024) / 1024)) + 1
        self.interpolation = interpolation_map[interpolation.upper()]   # 插值方式选项
        self.resize_anti_aliasing = resize_anti_aliasing
        self.compression = compression_map[compression.upper()]  # 压缩方式选项
        self.photometric = photometric_map[photometric.upper()]  # 颜色选项
        self.options = options
        self.channel = channel
        self.dtype = dtype
        self.default_value = default_value
        self.shapes = [
            (self.H // 2 ** level, self.W // 2 ** level)
            if self.channel == 0 else
            (self.H // 2 ** level, self.W // 2 ** level, self.channel)
            for level in range(self.level_count)
        ]
        self.tile_shapes = [
            (self.tile_size // 2 ** level, self.tile_size // 2 ** level)
            if self.channel == 0 else
            (self.tile_size // 2 ** level, self.tile_size // 2 ** level, self.channel)
            for level in range(self.level_count)
        ]
        self.resolutions = [(10000 / self.mpp / 2**level, 10000 / self.mpp / 2**level) for level in range(self.level_count)]
        self.tile_shape = self.tile_shapes[0]
        self.name = name or Path(output_path).name
        self.format = format or Path(output_path).suffix
        # self.desc = f'Aperio Image Library Fake\nABC |AppMag = {self.mag}|Filename = {self.name}|MPP = {self.mpp}'
        if self.format == '.svs':
            self.desc = f"Aperio Image Library v12.0.16\n{self.W}x{self.H} ({self.tile_size}x{self.tile_size}) |AppMag = {self.mag}|MPP = {self.mpp}|Filename = {self.name}"
        else:
            self.desc = f'Generic pyramidal\n{self.W}x{self.H} ({self.tile_size}x{self.tile_size}) |AppMag = {self.mag}|MPP = {self.mpp}|Filename = {self.name}'
        self.options = dict(
            subifds=0, dtype=self.dtype,
            photometric=self.photometric, compression=self.compression,
            planarconfig='CONTIG', metadata=None,
            resolutionunit='CENTIMETER',
            **options
        )
        self.thumb_w, self.thumb_h = self.W, self.H
        while max(self.thumb_w, self.thumb_h) > 768:
            self.thumb_w, self.thumb_h = self.thumb_w // 2, self.thumb_h // 2
        self.thumb_options = dict(
            shape=(self.thumb_h, self.thumb_w, 3),
            photometric=photometric_map['RGB'],
            compression=compression_map['LZW'],
            planarconfig='CONTIG',
            metadata=None,
            dtype=np.uint8,
            resolution=(10000 / self.mpp * self.thumb_w / self.W, 10000 / self.mpp * self.thumb_h / self.H),
            resolutionunit='CENTIMETER',
            **options,
        )

        # 这个必须按流式方法，一次性写入，我需要手动管理一个类似 ASAP 写图时的缓冲区的东西
        self._writer = tifffile.TiffWriter(output_path, bigtiff=True)
        self._buffer_path = f'{output_path}.buffer'
        self._buffer = open(self._buffer_path, 'wb')
        self._info_cache = {}
        self.cctx = zstd.ZstdCompressor(level=1)
        self.dctx = zstd.ZstdDecompressor()

        # 检查参数是否符合匹配要求，不符合直接报错
        try:
            sig = inspect.signature(self._writer.write)
            sig.bind(data=None, shape=None, tile=None, description=None, **self.options)  # 模拟 func(**options) 的参数匹配
        except TypeError as e:
            print(f"参数不匹配: {e}")
            raise e

    def write(self, tile: np.ndarray, x: int, y: int):
        assert tile.shape == self.tile_shape, f'要求写入数与维度数对齐 -- tile[{tile.shape}] -- writer[{self.tile_shape}]'
        assert tile.dtype == self.dtype, f'要求写入格式对齐 -- tile[{tile.dtype}] -- writer[{self.dtype}]'

        # 分层级存储
        info = []
        for level in range(self.level_count):
            tile = resize(tile, self.tile_shapes[level][:2], order=self.interpolation, anti_aliasing=self.resize_anti_aliasing, preserve_range=True).astype(self.dtype, copy=False)
            # tile = cv2.resize(tile, self.tile_shapes[level][:2], interpolation=self.interpolation)
            # 编码
            # success, buffer = cv2.imencode('.png', tile)
            # if not success: raise RuntimeError("图像压缩失败")
            # 使用 zstd 压缩格式
            buffer = self.cctx.compress(tile.flatten().tobytes())
            # 写入缓冲区
            pos_start = self._buffer.tell()
            self._buffer.write(buffer)  # 写入 PNG 数据
            pos_end = self._buffer.tell()
            info.append((pos_start, pos_end))
        # 记录写图信息
        self._info_cache[(x, y)] = info

    def finish(self):
        self._buffer.close()
        self._buffer = open(self._buffer_path, "rb")
        try:
            # 第 1 张，完整全图，带描述
            stream = self.load_buffer(level=0)
            self._writer.write(data=stream, shape=self.shapes[0], tile=self.tile_shape[:2], description=self.desc, resolution=self.resolutions[0], **self.options)
            # 若 svs 格式，第 2 张为缩略图
            if self.format == '.svs':
                image = self.load_image(level=-1)
                thumb = self.make_thumb(image)
                self._writer.write(data=thumb, **self.thumb_options)
            # 降分辨率tile图，从大到小
            for level in range(1, self.level_count):
                stream = self.load_buffer(level=level)
                self._writer.write(data=stream, shape=self.shapes[level], tile=self.tile_shape[:2], description='', resolution=self.resolutions[level], **self.options)
        except Exception as e:
            traceback.print_exc()
        finally:
            # 完毕
            self._writer.close()
            self._buffer.close()
            os.remove(self._buffer_path)

    def load_buffer(self, level: int):
        level %= self.level_count
        space = np.ones(self.tile_shapes[level], self.dtype) * self.default_value
        H, W = self.shapes[0][:2]
        h, w = self.shapes[level][:2]
        # 使用标准尺寸遍历
        z = 2**level
        t = self.tile_size // z
        for y in range(0, h, self.tile_size):
            for x in range(0, w, self.tile_size):
                out_patch = np.empty(self.tile_shape, self.dtype)
                # level > 1 时，先合并图块，再一块输出为流
                for i, j in [(i, j) for i in range(z) for j in range(z)]:
                    Y = y * z + i * self.tile_size
                    X = x * z + j * self.tile_size
                    if (X, Y) not in self._info_cache:
                        patch = space
                    else:
                        pos_start, pos_end = self._info_cache[(X, Y)][level]
                        self._buffer.seek(pos_start)
                        buffer = self._buffer.read(pos_end - pos_start)
                        image_bytes = self.dctx.decompress(buffer)
                        patch = np.frombuffer(image_bytes, dtype=self.dtype).reshape(self.tile_shapes[level])
                    out_patch[t*i: t*(i+1), t*j: t*(j+1), ...] = patch
                yield out_patch

    def load_image(self, level: int):
        stream = self.load_buffer(level=level)
        h, w = self.shapes[level][:2]
        ty, tx = self.tile_shape[: 2]
        shape = (h+-h%ty, w+-w%tx, *self.shapes[level][2:])
        image = np.zeros(shape, dtype=self.dtype)
        for y in range(0, h, ty):
            for x in range(0, w, tx):
                tile = next(stream)
                image[y: y+ty, x: x+tx, ...] = tile
        return image

    def make_thumb(self, image: np.ndarray):
        if np.issubdtype(image.dtype, np.floating):
            image = (image.clip(0, 1) * 255).round().astype(np.uint8)
        image = image.astype(np.uint8)
        if image.ndim == 2:
            image = image[..., None]
        if image.shape[2] < 3:
            image = np.concatenate([image, np.repeat(image[..., [-1]], 3 - image.shape[2], 2)], 2)
        elif image.shape[2] > 3:
            image = image[..., :3]
        image = cv2.resize(image, (self.thumb_w, self.thumb_h))
        return image

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type and not exc_val and not exc_tb:
            self.finish()
        else:
            traceback.print_exc()
            try:
                self._writer.close()
            except Exception as e:
                pass
            if not self._buffer.closed: self._buffer.close()
        return False
