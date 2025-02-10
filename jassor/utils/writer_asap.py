import multiresolutionimageinterface as mir
import numpy as np
import traceback


class SlideWriter:
    def __init__(self, output_path: str, tile_size: int, dimensions: tuple, spacing: float, color_type: str):
        self.output_path = output_path
        self.tile_size = tile_size
        self.W, self.H = dimensions
        # 要求横纵分辨率一致
        self.spacing = spacing
        self.color_type = color_type

        # 以下进入准备部分
        self._writer = mir.MultiResolutionImageWriter()
        self._writer.openFile(self.output_path)
        self._writer.setTileSize(self.tile_size)

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

        # 两个版本间存在一些命名不同
        self._writer.setCompression(mir.Compression_LZW)
        self._writer.setDataType(mir.DataType_UChar)
        self._writer.setInterpolation(mir.Interpolation_NearestNeighbor)
        # 可以在这个接口类下找到各种各样的可写类型
        # https://github.com/computationalpathologygroup/ASAP/blob/develop/multiresolutionimageinterface/MultiResolutionImageWriter.h
        # self._writer.setDownsamplePerLevel(4)
        # self._writer.setMaxNumberOfPyramidLevels(3)
        # color_type: Monochrome, RGB, RGBA, Indexed
        color_type = {
            'MONOCHROME': mir.ColorType_Monochrome,
            'RGB': mir.ColorType_RGB,
            'RGBA': mir.ColorType_RGBA,
            'INDEXED': mir.ColorType_Indexed,
        }[self.color_type.upper()]

        self._writer.setColorType(color_type)
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
