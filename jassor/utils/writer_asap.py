from collections import defaultdict

import multiresolutionimageinterface as mir
import numpy as np
import traceback


class SlideWriter:
    def __init__(self, output_path: str, tile_size: int, dimensions: tuple, spacing: float, **options: str):
        self.output_path = output_path
        self.tile_size = tile_size
        self.W, self.H = dimensions
        # 要求横纵分辨率一致
        self.spacing = spacing

        # 以下进入准备部分
        self._writer = mir.MultiResolutionImageWriter()
        self._writer.openFile(self.output_path)

        # 可以在这个接口类下找到各种各样的可写类型
        # https://github.com/computationalpathologygroup/ASAP/blob/develop/multiresolutionimageinterface/MultiResolutionImageWriter.h
        # self._writer.setDownsamplePerLevel(4)
        # self._writer.setMaxNumberOfPyramidLevels(3)
        # color_type: Monochrome, RGB, RGBA, Indexed

        options = defaultdict(lambda: None, **options)
        color_type = options['color_type'] or 'MONOCHROME'
        data_type = options['data_type'] or 'UCHAR'
        compression = options['compression'] or 'LZW'
        interpolation = options['interpolation'] or 'NEAREST'

        self._writer.setColorType(color_type_map[color_type.upper()])
        self._writer.setDataType(data_type_map[data_type.upper()])
        self._writer.setCompression(compression_map[compression.upper()])
        self._writer.setInterpolation(interpolation_map[interpolation.upper()])

        # 两个版本间存在一些命名不同
        # self._writer.setCompression(mir.LZW)
        # self._writer.setDataType(mir.UChar)
        # self._writer.setInterpolation(mir.NearestNeighbor)
        # # color_type: Monochrome, RGB, RGBA, Indexed
        # color_type = {
        #     'MONOCHROME': mir.Monochrome,
        #     'RGB': mir.RGB,
        #     'RGBA': mir.RGBA,
        #     'INDEXED': mir.Indexed,
        # }[self.color_type.upper()]
        # options = {
        #     "compression": "jpeg",
        #     "jpeg_quality": 90,
        #     "tile_size": 512,
        #     "BigTIFF": True
        # }

        self._writer.setTileSize(self.tile_size)
        self._writer.writeImageInformation(self.W, self.H)
        pixel_size_vec = mir.vector_double()
        pixel_size_vec.push_back(self.spacing)
        pixel_size_vec.push_back(self.spacing)
        self._writer.setSpacing(pixel_size_vec)

    def write(self, tile: np.ndarray, x: int, y: int):
        assert tile.shape[0] == tile.shape[1] == self.tile_size, f'要求写入数与维度数对齐{tile.shape} -- {self.tile_size}'
        self._writer.writeBaseImagePartToLocation(tile.flatten().astype('uint8'), x=int(x), y=int(y))

    def finish(self):
        self._writer.finishImage()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not exc_type and not exc_val and not exc_tb:
            self.finish()
        else:
            traceback.print_exc()
        return False


color_type_map = {
    'INVALID': mir.ColorType_InvalidColorType,
    'MONOCHROME': mir.ColorType_Monochrome,
    'RGB': mir.ColorType_RGB,
    'RGBA': mir.ColorType_RGBA,
    'INDEXED': mir.ColorType_Indexed,
}
data_type_map = {
    'INVALID': mir.DataType_InvalidDataType,
    'UCHAR': mir.DataType_UChar,
    'UINT16': mir.DataType_UInt16,
    'UINT32': mir.DataType_UInt32,
    'FLOAT': mir.DataType_Float,
}
compression_map = {
    'RAW': mir.Compression_RAW,
    'JPEG': mir.Compression_JPEG,
    'LZW': mir.Compression_LZW,
    'JPEG2000': mir.Compression_JPEG2000,
}
interpolation_map = {
    'LINEAR': mir.Interpolation_Linear,
    'NEAREST': mir.Interpolation_NearestNeighbor,
}
