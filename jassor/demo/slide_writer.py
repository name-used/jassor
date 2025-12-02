from pathlib import Path
import jassor.utils as J
from jassor.components.data.reader_tiff import TiffSlide
from jassor.components.data.reader_openslide import OpenSlide
from jassor.components.data.reader_asap import AsapSlide
import numpy as np

k = 512
w = 5900
h = 3700
output_root = Path(rf'../../cache/slide_write')
output_root.mkdir(exist_ok=True)


def main():
    print('第一段程序测试写出灰度图')
    demo1(output_root / rf'test1.tif')
    # input('输入任意字符以继续...')
    # print('第二段程序测试写出RGB图')
    # demo2(output_root / rf'test1.tif')
    # input('输入任意字符以继续...')
    # print('第三段程序测试写出uint16图')
    # demo3(output_root / rf'test1.tif')
    # input('输入任意字符以继续...')
    # print('第三段程序测试写出int64图')
    # demo4(output_root / rf'test1.tif')
    # input('输入任意字符以继续...')
    # print('第三段程序测试写出多通道图')
    # demo5(output_root / rf'test1.tif')


def demo1(path):
    # 现在使用 TIFFFILE 写 SVS 图
    # 在 TIFFFILE 定义中，灰度图的定义是 MINISBLACK
    # 同时，本地封装定义 channel==0 时形状为 (height, width)
    # 当 channel >= 1 时，形状为 (height, width, channel)
    with J.SlideWriter(
        output_path=path,
        tile_size=k,
        dimensions=(w, h),
        level_count=5,
        mpp=1,
        mag=40,
        photometric='MINISBLACK',
        channel=0,
    ) as writer:
        for y in range(0, h, k):
            for x in range(0, w, k):
                patch = random_patch(k, 1, 255, np.uint8)[..., 0]
                # print(f'color_{x}_{y}:{patch[0, 0]}')
                writer.write(patch, x, y)

    # 为展示多样性支持，例程中分别使用 openslide、tiffslide、asapslide 读取缩略图
    slide = TiffSlide(path)
    print(slide.level_count, slide.dimension(-1), slide.downsample(-1), [slide.downsample(level) for level in range(slide.level_count)])
    # print(slide.slide.properties)
    thumb = slide.thumb(level=0)
    J.plot(thumb)


def demo2(path):
    with J.SlideWriter(
        output_path=path,
        tile_size=k,
        dimensions=(w, h),
        level_count=2,
        mpp=1,
        mag=40,
        photometric='RGB',
        channel=3,
    ) as writer:
        for y in range(0, h, k):
            for x in range(0, w, k):
                patch = random_patch(k, 3, 255, np.uint8)
                # print(f'color_{x}_{y}:{patch[0, 0]}')
                writer.write(patch, x, y)

    # 为展示多样性支持，例程中分别使用 openslide、tiffslide、asapslide 读取缩略图
    slide = AsapSlide(path)
    print(slide.level_count, slide.dimension(-1), slide.downsample(-1))
    thumb = slide.thumb(level=0)
    J.plot(thumb)


def demo3(path):
    with J.SlideWriter(
        output_path=path,
        tile_size=k,
        dimensions=(w, h),
        level_count=2,
        mpp=1,
        mag=40,
        photometric='RGB',
        channel=3,
        dtype=np.uint16
    ) as writer:
        for y in range(0, h, k):
            for x in range(0, w, k):
                patch = random_patch(k, 3, 50000, np.uint16)
                # print(f'color_{x}_{y}:{patch[0, 0]}')
                writer.write(patch, x, y)

    # ASAP 不能读 uint16 的图，plot 对于大于 255 的数值也不能正常显示
    slide = TiffSlide(path)
    print(slide.level_count, slide.dimension(-1), slide.downsample(-1))
    thumb = slide.thumb(level=0)
    print(thumb.max(), thumb.dtype, thumb.shape)
    J.plots([thumb // 256, thumb % 256])


def demo4(path):
    with J.SlideWriter(
        output_path=path,
        tile_size=k,
        dimensions=(w, h),
        level_count=2,
        mpp=1,
        mag=40,
        photometric='RGB',
        channel=3,
        dtype=np.int64
    ) as writer:
        for y in range(0, h, k):
            for x in range(0, w, k):
                patch = random_patch(k, 3, 50000, np.int64)
                # print(f'color_{x}_{y}:{patch[0, 0]}')
                writer.write(patch, x, y)

    # 甚至可以存储 int64
    slide = TiffSlide(path)
    print(slide.level_count, slide.dimension(-1), slide.downsample(-1))
    thumb = slide.thumb(level=0)
    print(thumb.max(), thumb.dtype, thumb.shape)


def demo5(path):
    with J.SlideWriter(
        output_path=path,
        tile_size=k,
        dimensions=(w, h),
        level_count=2,
        mpp=1,
        mag=40,
        photometric='RGB',
        channel=5,
        dtype=np.uint8
    ) as writer:
        for y in range(0, h, k):
            for x in range(0, w, k):
                patch = random_patch(k, 5, 255, np.uint8)
                # print(f'color_{x}_{y}:{patch[0, 0]}')
                writer.write(patch, x, y)

    # 也可以存储多通道（但这样就没办法可视化了）
    slide = TiffSlide(path)
    print(slide.level_count, slide.dimension(-1), slide.downsample(-1))
    thumb = slide.thumb(level=0)
    print(thumb.max(), thumb.dtype, thumb.shape)


def random_patch(patch_size: int, channel: int, max_value: int, dtype: type):
    basic = np.ones((patch_size, patch_size, 1))
    color = np.random.random(channel)[None, None, :]
    patch = basic * (color * max_value).round().astype(int)
    return patch.astype(dtype)


if __name__ == '__main__':
    main()
