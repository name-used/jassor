# @Time    : 2022.03.17
# @Author  : Bohrium.Kwong
# @Licence : bio-totem

import os
import multiresolutionimageinterface as mir
from PIL import Image
import numpy as np

Image.MAX_IMAGE_PIXELS = 200000000


class Slide(mir.MultiResolutionImage):
    def __init__(self, svs_file, level=2):
        """
        open svs file with open-slide
        :param svs_file: svs file, absolute path
        :return: slide
        """
        # super().__init__(svs_file)
        self._filepath = svs_file
        self._basename = os.path.basename(svs_file).split('.')[0]
        reader = mir.MultiResolutionImageReader()
        self.slide = reader.open(svs_file)
        self._level = level

    def getDimensions(self):
        """
        return (w, h)
        """
        return self.slide.getDimensions()

    def get_basename(self):
        """
        return svs file basename, not contain file suffix
        :return:
        """

        return self._basename

    def get_filepath(self):
        """
        get absolute svs file
        :return:
        """

        return self._filepath

    def get_level(self):
        """
        return level
        :return:
        """

        return self._level

    def get_level_count(self):
        """
        return number of levels
        :return:
        """

        return self.slide.getNumberOfLevels()

    def get_level_downsample(self, level=2):
        """
        get the expected level downsample, default level two
        :param level: level, default 2
        :return: the level downsample
        """

        return self.slide.getLevelDownsample(level)

    def get_level_dimension(self, level=2):
        """
        get the expected level dimension, default level two
        :param level: level, default 0
        :return:
        """

        return self.slide.getLevelDimensions(level)

    # def svs_to_png(self,save_dir):
    #     """
    #     convert svs to png
    #     :return:
    #     """
    #     self.get_thumb().save(save_dir)

    # def expand_img(self, im, size, value=(0, 0, 0)):
    #     """
    #     expand the image
    #     :param im: the image want to expand
    #     :param size: tuple, the size of expand
    #     :param value: tuple, the pixel value at the expand region
    #     :return: the expanded image
    #     """

    #     im_new = Image.new("RGB", size, value)
    #     im_new.paste(im, (0, 0))

    #     return im_new

    def get_mpp(self):
        """
        get the value of mpp
        :return: 0.00025/0.0005
        """
        mpp = self.slide.getProperty('openslide.mpp-x')
        if mpp == '':
            mpp = self.slide.getSpacing()[0]

        return np.float(mpp) / 1000

    def get_thumb(self, level=2):
        """
        get thumb image
        :return:
        """
        tile_size = self.slide.getLevelDimensions(level)
        tile = self.slide.getUCharPatch(
            startX=0, startY=0, width=tile_size[0], height=tile_size[1], level=level
        )

        return tile

    def read_region(self, location: tuple, level: int, size: tuple):
        """
        get the tile base on the input coordinate tuple and level value and tile_size tuple
        tuple is requried as (x,y)
        :return: tle in np.array format
        """
        tile = self.slide.getUCharPatch(
            startX=location[0], startY=location[1], width=size[0], height=size[1], level=level
        )

        return tile

    def get_best_level_downsample(self, downsample: int):
        """
        get the best downsample level for input target downsample value
        :return:
        """
        return self.slide.getBestLevelForDownSample(downsample)
