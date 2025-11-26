import PIL.Image
import numpy as np
from jassor.components import data
import jassor.utils as J


def main():
    # print('第一段程序展示基本使用方法（以 .jpg 图片为例）')
    # demo1()
    # input('输入任意字符以继续...')
    # print('第二段程序展示核心使用方法（以 .tif 数据为例）')
    # demo2()
    # input('输入任意字符以继续...')
    print('第三段程序展示切图方法')
    demo3()


def demo1():
    image = PIL.Image.open(rf'../../resources/test.jpg')
    # image = np.asarray(image)
    samples = data.sample_image(image, 1000, 800)
    dataset = data.SingleDataset(source=image, samples=samples)
    patches = [patch for patch in dataset]
    J.plots(patches)


def demo2():
    image = PIL.Image.open(rf'../../resources/test.jpg')
    image = np.asarray(image)
    J.image2slide(image, rf'../../resources/test.tif')

    slide_reader = data.load(rf'../../resources/test.tif')
    samples = data.sample_slide(slide_reader, 1, 500, 400)
    dataset = data.SingleDataset(source=slide_reader, samples=samples)
    patches = [patch for patch in dataset]
    J.plots(patches)


def demo3():
    reader = data.TiffSlide(rf'../../resources/test.tif')
    region = reader.region(0, 400, 0, 1600, 800)
    s1 = data.crop(reader, center=(1000, 400), size=(1200, 800), degree=0, scale=1, nearest=False, pad_item=0)
    s2 = data.crop(reader, center=(1000, 400), size=(1200, 800), degree=0, scale=2, nearest=False, pad_item=100)
    s3 = data.crop(reader, center=(1000, 400), size=(1200, 800), degree=15, scale=1, nearest=False, pad_item=[255, 0, 0])
    J.plots([region, s1, s2, s3], ticks=False)


if __name__ == '__main__':
    main()
