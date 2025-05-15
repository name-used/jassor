import jassor.utils as J
from jassor.components.data.reader_tiff import TiffSlide
import numpy as np


def main():
    path = rf'./test.tif'
    k = 512
    w = 2048
    h = 1024
    # color_type in ['INVALID', 'MONOCHROME', 'RGB', 'RGBA', 'INDEXED']
    # data_type in ['INVALID', 'UCHAR', 'UINT16', 'UINT32', 'FLOAT']
    # compression in ['RAW', 'JPEG', 'LZW', 'JPEG2000']
    # interpolation in ['LINEAR', 'NEAREST']
    with J.SlideWriter(
        output_path=path,
        tile_size=k,
        dimensions=(w, h),
        spacing=1,
    ) as writer:
        for y in range(0, h, k):
            for x in range(0, w, k):
                patch = random_patch(k, 1, 255, np.uint8)[..., 0]
                # patch[:, :, 3] = 120
                print(f'color_{x}_{y}:{patch[0, 0]}')
                writer.write(patch, x, y)

    slide = TiffSlide(path)
    thumb = slide.thumb(level=0)
    for y in range(0, h, k):
        for x in range(0, w, k):
            print(thumb[y, x])
    J.plot(thumb)


def random_patch(patch_size: int, channel: int, max_value: int, dtype: type):
    basic = np.ones((patch_size, patch_size, 1))
    color = np.random.random(channel)[None, None, :]
    patch = basic * (color * max_value).round().astype(int)
    return patch.astype(dtype)


if __name__ == '__main__':
    main()
