import multiresolutionimageinterface as mir
import numpy as np
import traceback


class SlideWriter(mir.MultiResolutionImage):
    def __init__(self, output_path: str, tile_size: int, dimensions: tuple, spacing: float, *args, **kwargs):
        super(SlideWriter, self).__init__()
        self.output_path = output_path
        self.tile_size = tile_size
        self.W, self.H = dimensions
        # 要求横纵分辨率一致
        self.spacing = spacing

    def __enter__(self):
        self._writer = mir.MultiResolutionImageWriter()
        self._writer.openFile(self.output_path)
        self._writer.setTileSize(self.tile_size)
        self._writer.setCompression(mir.LZW)
        self._writer.setDataType(mir.UChar)
        self._writer.setInterpolation(mir.NearestNeighbor)
        self._writer.setColorType(mir.Monochrome)
        self._writer.writeImageInformation(self.W, self.H)
        pixel_size_vec = mir.vector_double()
        pixel_size_vec.push_back(self.spacing)
        pixel_size_vec.push_back(self.spacing)
        self._writer.setSpacing(pixel_size_vec)
        return self

    def write(self, tile: np.ndarray, x: int, y: int):
        assert tile.shape[0] == tile.shape[1] == self.tile_size, '要求写入数与维度数对齐'
        self._writer.writeBaseImagePartToLocation(tile.flatten().astype('uint8'), x=int(x), y=int(y))

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._writer.finishImage()
        except Exception:
            traceback.print_exc()
        return False
