# https://blog.csdn.net/ONE_SIX_MIX/article/details/123930973?spm=1001.2014.3001.5506
# @creator: ONE_SIX_MIX
import time
import numpy as np
import tifffile
import cv2


def gen_im(size_hw):
    # 带编号的图块生成器，用于观察tile块的顺序
    im_i = 0
    while True:
        im = np.zeros([*size_hw, 3], np.uint8)+255
        im[:60, :60, :2] = 0
        im[:60, -60:, 2] = 0
        im[-60:, -60:, 1:] = 0
        im[-60:, :60, 1] = 0
        im = cv2.putText(im, str(im_i), (size_hw[1]//4, size_hw[0]//2), cv2.FONT_HERSHEY_PLAIN, 3, color=(0, 0, 0), thickness=3)
        im_i += 1
        # 注意，不要使用稀疏格式，会导致加载缓慢的问题
        yield im


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
#


def gen_pyramid_tiff(out_file):

    # 缩略图
    thumbnail_im = np.zeros([762, 762, 3], dtype=np.uint8)
    thumbnail_im = cv2.putText(thumbnail_im, 'thumbnail', (thumbnail_im.shape[1]//4, thumbnail_im.shape[0]//2), cv2.FONT_HERSHEY_PLAIN, 6, color=(255, 0, 0), thickness=3)
    # 标签图
    label_im = np.zeros([762, 762, 3], dtype=np.uint8)
    label_im = cv2.putText(label_im, 'label', (label_im.shape[1]//4, label_im.shape[0]//2), cv2.FONT_HERSHEY_PLAIN, 6, color=(0, 255, 0), thickness=3)
    # 宏观图
    macro_im = np.zeros([762, 762, 3], dtype=np.uint8)
    macro_im = cv2.putText(macro_im, 'macro', (macro_im.shape[1]//4, macro_im.shape[0]//2), cv2.FONT_HERSHEY_PLAIN, 6, color=(0, 0, 255), thickness=3)

    # tile 大小
    tile_hw = np.int64([512, 512])

    # 要需要的金字塔分辨率
    # multi_hw = np.int64([(10240, 10240), (7680, 7680), (2560, 2560), (1024, 1024), (512, 512)])
    multi_hw = np.int64([(10240, 10240), (7680, 7680), (2560, 2560), (1024, 1024), (513, 513)])
    # multi_hw = np.int64([(10240, 10240), (5120, 5120), (2560, 2560), (1280, 1280), (640, 640)])

    # 指定mpp值
    mpp = 0.25
    # 指定缩放倍率
    mag = 40
    # 换算mpp值到分辨率
    resolution = [10000 / mpp, 10000 / mpp, 'CENTIMETER']
    # 指定图像名字
    filename = 'ASD'

    # 尝试写入 svs 格式
    with tifffile.TiffWriter(out_file, bigtiff=True) as tif:

        thw = tile_hw.tolist()

        # outcolorspace 要保持为默认的 YCbCr，不能使用rgb，否则颜色会异常
        # 95 是默认JPEG质量，值域是 0-100，值越大越接近无损
        # compression = ['JPEG', 95, dict(outcolorspace='YCbCr')]
        # compression = 'JPEG'
        # kwargs = dict(subifds=0, photometric='rgb', planarconfig='CONTIG', compression=compression, dtype=np.uint8, metadata=None)
        kwargs = dict(subifds=0, dtype=np.uint8, metadata=None)

        for i, hw in enumerate(multi_hw):
            gen = gen_im(tile_hw)

            hw = hw.tolist()

            if i == 0:
                desc = svs_desc.format(mag=mag, filename=filename, mpp=mpp)
                # desc = ''

                tif.write(data=gen, shape=(*hw, 3), tile=thw[::-1], resolution=resolution, description=desc, **kwargs)
                # 写入缩略图
                # tif.write(data=thumbnail_im, description='', **kwargs)

            else:
                tif.write(data=gen, shape=(*hw, 3), tile=thw[::-1], resolution=resolution, description='', **kwargs)

        # # # 写入标签图
        # tif.write(data=label_im, subfiletype=1, description=label_desc.format(W=label_im.shape[1], H=label_im.shape[0]), **kwargs)
        # # # 写入宏观图
        # tif.write(data=macro_im, subfiletype=9, description=macro_desc.format(W=macro_im.shape[1], H=macro_im.shape[0]), **kwargs)


t1 = time.perf_counter()
gen_pyramid_tiff('a9.svs')
print(time.perf_counter() - t1)
