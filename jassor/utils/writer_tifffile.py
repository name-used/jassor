import inspect
import os
import tifffile
import numpy as np
import cv2
import traceback


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
        spacing: float,
        level_count: int = 5,
        interpolation: int = cv2.INTER_NEAREST,
        channel: int = 0,
        dtype: type = np.uint8,
        **options: str
    ):
        self.output_path = output_path
        self.tile_size = tile_size
        self.W, self.H = dimensions
        # 要求横纵分辨率一致
        self.spacing = spacing
        self.level_count = level_count
        self.interpolation = interpolation
        self.options = options
        self.channel = channel
        self.dtype = dtype
        self.shapes = [
            (self.H // 2**level, self.W // 2**level)
            if self.channel == 0 else
            (self.H // 2**level, self.W // 2**level, self.channel)
            for level in range(level_count)
        ]
        self.tile_shapes = [
            (self.tile_size // 2**level, self.tile_size // 2**level)
            if self.channel == 0 else
            (self.tile_size // 2**level, self.tile_size // 2**level, self.channel)
            for level in range(level_count)
        ]
        self.tile_shape = self.tile_shapes[0]

        # 这个必须按流式方法，一次性写入，我需要手动管理一个类似 ASAP 写图时的缓冲区的东西
        self._writer = tifffile.TiffWriter(output_path, bigtiff=True)
        self._buffer_path = f'{output_path}.buffer'
        self._buffer = open(self._buffer_path, 'wb')
        self._info_cache = {}

        # 检查参数是否符合匹配要求，不符合直接报错
        try:
            sig = inspect.signature(self._writer.write)
            sig.bind(data=None, shape=None, tile=None, dtype=None, **self.options)  # 模拟 func(**options) 的参数匹配
        except TypeError as e:
            print(f"参数不匹配: {e}")
            raise e

    def write(self, tile: np.ndarray, x: int, y: int):
        assert tile.shape == self.tile_shape, f'要求写入数与维度数对齐{tile.shape} -- {self.tile_shape}'

        # 分层级存储
        info = []
        ks = [self.tile_size // 2**level for level in range(self.level_count)]
        for level in range(self.level_count):
            k = ks[level]
            tile = cv2.resize(tile, (k, k), interpolation=self.interpolation)
            # 编码
            success, buffer = cv2.imencode('.png', tile)
            if not success: raise RuntimeError("图像压缩失败")
            # 写入缓冲区
            pos_start = self._buffer.tell()
            self._buffer.write(buffer.tobytes())                  # 写入 PNG 数据
            pos_end = self._buffer.tell()
            info.append((pos_start, pos_end))
        # 记录写图信息
        self._info_cache[(x, y)] = info

    def finish(self):
        self._buffer.close()
        self._buffer = open(self._buffer_path, "rb")
        # 第 1 张，完整全图
        stream = self.load_buffer(level=0)
        self._writer.write(data=stream, shape=self.shapes[0], tile=self.tile_shapes[0], dtype=self.dtype, description='FullImage', **self.options)
        # 第 2 张，缩略图
        stream = self.load_buffer(level=-1)
        self._writer.write(data=stream, shape=self.shapes[-1], tile=self.tile_shapes[-1], dtype=self.dtype, description='Thumbnail', **self.options)
        # 第 3 到第 N-2 张，降分辨率tile图，必须使用从大到小顺序
        for level in range(1, self.level_count):
            stream = self.load_buffer(level=level)
            self._writer.write(data=stream, shape=self.shapes[level], tile=self.tile_shapes[level], dtype=self.dtype, description=f'level{level}', **self.options)
        # 第 N-1 张 label 图 (没意义)
        self._writer.write(data=np.zeros((64, 64), np.uint8), shape=(64, 64), tile=(64, 64), dtype=self.dtype, description=f'label', **self.options)
        # 第 N 张 marco 图 (不知道什么作用)
        stream = self.load_buffer(level=-1)
        self._writer.write(data=stream, shape=self.shapes[-1], tile=self.tile_shapes[-1], dtype=self.dtype, description='Thumbnail', **self.options)
        # 完毕
        self._writer.close()
        self._buffer.close()
        os.remove(self._buffer_path)

    def load_buffer(self, level: int):
        space = np.zeros(self.tile_shape, self.dtype)
        for y in range(0, self.H, self.tile_size):
            for x in range(0, self.W, self.tile_size):
                if (x, y) not in self._info_cache:
                    yield space
                    continue
                pos_start, pos_end = self._info_cache[(x, y)][level]
                self._buffer.seek(pos_start)
                buffered_data = self._buffer.read(pos_end - pos_start)
                img_array = np.frombuffer(buffered_data, dtype=self.dtype)
                img = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
                yield img

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type and not exc_val and not exc_tb:
            self.finish()
        else:
            traceback.print_exc()
        return False


photometric_map = {
    # 来自 GPT
    'MINISWHITE': 0,        # 单通道图像中，0 表示白色，最大值表示黑色（老式习惯）
    'MINISBLACK': 1,        # 单通道图像中，0 表示黑色，最大值表示白色（现代标准）
    'RGB': 2,               # 多通道彩色图像，3 个通道分别表示 R、G、B
    'PALETTE': 3,           # 图像值为颜色查找表（colormap）中的索引
    'MASK': 4,              # 通常用于蒙版或 alpha
    'SEPARATED': 5,         # CMYK 色彩空间（青品黄黑）
    'YCBCR': 6,             # YCbCr 色彩空间（通常用于 JPEG 编码）
    'CIELAB': 8,            # Lab 色彩空间
    'CFA': 32803,           # Color Filter Array，传感器原始图像（如 Bayer 图）
    'LOGHUFFMAN': 32844,    # 用于 LogLuv 图像
    'LINEARRAW': 34892,     # 用于 Raw 图像数据
    # 在 tifffile 中还可能支持字符串形式，比如：'minisblack'、'rgb'、'palette'、'cfa' 等。
}
compression_map = {
    'NONE': 1,              # 单通道图像中，0 表示白色，最大值表示黑色（老式习惯）
    'LZW': 5,               # Lempel-Ziv-Welch 压缩
    'JPEG': 6,              # JPEG 压缩（通常与 YCbCr 配合）
    'JPEGOLD': 7,           # 老式 JPEG（不推荐）
    'ZLIB': 8,              # zlib 压缩
    'DEFLATE': 32946,       # ADOBE 定义的 deflate 算法
    'PACKBITS': 32773,      # 一种简单的 RLE 压缩
    'LERC': 34925,          # Limited Error Raster Compression，用于 GIS
    'ZSTD': 50001,          # Facebook 提出的压缩算法
    'LZMA': 50002,          # Lempel-Ziv-Markov 压缩
    'WEBP': 50003,          # 用于 Web 图像压缩
    'auto': 'auto',         # 自动选择（仅在某些 tifffile 函数中支持）
}
