import tifffile
import numpy as np
import zarr
from PIL import Image


class ZarrSlide:
    def __init__(self, image_path):
        self.image_path = image_path
        self.store = tifffile.imread(image_path, aszarr=True)

        self._level_dimensions = []
        self._level_downsamples = []

        slide = zarr.open(self.store)
        base_shape = slide['0'].shape  # (H, W, C)
        base_height, base_width = base_shape[1:3]
        for level in slide:
            # level in ['0', '1', ...]
            height, width = slide[level].shape[1:3]
            self._level_dimensions.append((width, height))
            downsample = base_width / width
            self._level_downsamples.append(downsample)

        self.properties = {
            "openslide.vendor": "zarrslide",
            "zarrslide.file": str(image_path),
        }

    @property
    def level_count(self):
        return len(self._level_dimensions)

    @property
    def level_dimensions(self):
        return self._level_dimensions

    @property
    def level_downsamples(self):
        return self._level_downsamples

    @property
    def dimensions(self):
        return self._level_dimensions[0]

    def read_region(self, location, level, size):
        """ Mimics OpenSlide read_region:
        Args:
            location: (x, y) coordinates at level 0
            level: pyramid level index
            size: (width, height) at target level
        Returns:
            PIL.Image
        """
        x0, y0 = location
        w, h = size

        # Calculate coordinates at target level
        scale = self.level_downsamples[level]
        x = int(x0 / scale)
        y = int(y0 / scale)
        width, height = self.level_dimensions[level]

        x_end = min(x + w, width)
        y_end = min(y + h, height)

        slide = zarr.open(self.store)
        # 通道名称：
        # Hoechst, AF1, CD31, CD45, CD68, Argo550, CD4, FOXP3, CD8a, CD45RO, CD20, PD-L1, CD3e, CD163, E-cadherin, PD-1, Ki67, Pan-CK, SMA
        # 取第 0、12、8 通道，即 Hoechst, CD3e, CD8a
        scn_hoechst = np.asarray(slide[str(level)][0, y: y_end, x: x_end])
        scn_cd3e = np.asarray(slide[str(level)][12, y: y_end, x: x_end])
        scn_cd8a = np.asarray(slide[str(level)][8, y: y_end, x: x_end])
        region = np.stack([scn_hoechst, scn_cd3e, scn_cd8a], axis=2)

        # Pad if region is smaller than requested
        pad_w = w - (x_end - x)
        pad_h = h - (y_end - y)
        if pad_w > 0 or pad_h > 0:
            region = np.pad(
                region,
                ((0, pad_h), (0, pad_w), (0, 0)),
                mode='constant',
                constant_values=0
            )

        return region

    def get_best_level_for_downsample(self, downsample):
        """ Return best level index for a given downsample factor """
        diffs = [abs(ds - downsample) for ds in self.level_downsamples]
        return int(np.argmin(diffs))


if __name__ == '__main__':
    # my_slide = ZarrSlide(rf'D:\jassor_resources\align_data\temp\18459_LSP10353_US_SCAN_OR_001__093059-registered.ome.tif')
    my_slide = ZarrSlide(rf'D:\jassor_resources\align_data\CRC01\P37_S29_A24_C59kX_E15_20220106_014304_946511-zlib.ome.tiff')
    my_region = my_slide.read_region(location=(0, 0), level=4, size=(3000, 3000))
    import jassor.utils as J
    J.plot(my_region)
