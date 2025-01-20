import os

import numpy as np
import tifffile
import cv2


'''
svs格式定义，TIFF或BIGTIFF，不能使用subifds
第1张，全分辨率tile图，需设定desc
第2张，缩略图
第3到第N-2张，降分辨率tile图，必须使用从大到小顺序
第N-1张，label图，需设定标志(ReducedImage 1 (0x1))，需设定desc
第N张，marco图，需设定标志 (ReducedImage 1 (0x1), Macro 8 (0x8))，需设定desc
'''


# 一些svs定义
svs_desc = 'Aperio Image Library Fake\nABC |AppMag = {mag}|Filename = {filename}|MPP = {mpp}'
label_desc = 'Aperio Image Library Fake\nlabel {W}x{H}'
macro_desc = 'Aperio Image Library Fake\nmacro {W}x{H}'


def image2slide(image: np.ndarray, out_file: str, mpp: float = 0.5) -> None:

    H, W, _ = image.shape
    w, h = W, H

    # 要需要的金字塔分辨率
    while w > 1000 or h > 1000:
        w //= 2
        h //= 2

    # tile 大小
    t = 64

    # 指定mpp值
    mpp = mpp
    # 指定缩放倍率 (目前为止我们用的都是 0.5 * 20 = 10)
    mag = round(10 / mpp)
    # 换算mpp值到分辨率
    resolution = [10000 / mpp, 10000 / mpp, 'CENTIMETER']
    # 指定图像名字
    filename = os.path.basename(out_file)

    # 尝试写入 svs 格式
    with tifffile.TiffWriter(out_file, bigtiff=True) as tif:

        # outcolorspace 要保持为默认的 YCbCr，不能使用rgb，否则颜色会异常
        # 95 是默认JPEG质量，值域是 0-100，值越大越接近无损
        compression = ['JPEG', 95, dict(outcolorspace='YCbCr')]
        # compression = 'JPEG'
        kwargs = dict(subifds=0, photometric='rgb', planarconfig='CONTIG', compression=compression, dtype=np.uint8, metadata=None)

        tif.write(data=image, shape=(H, W, 3), tile=(t, t), resolution=resolution, description=svs_desc.format(mag=mag, filename=filename, mpp=mpp), **kwargs)
        image = cv2.resize(image, (w, h))
        tif.write(data=image, shape=(h, w, 3), tile=(t, t), resolution=resolution, description='', **kwargs)
