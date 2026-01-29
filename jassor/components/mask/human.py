import sys
import os.path
from typing import Union
from pathlib import Path
import urllib.request
import cv2
import numpy as np
import onnxruntime


# 来自 modnet 的权重
# 仓库地址：https://github.com/ZHKKKe/MODNet
# 权重地址：https://drive.google.com/drive/folders/1umYmlCulvIFNaqPjwod1SayFmSRHziyR
# 使用 Apache 2.0 协议
# 谷歌云使用动态链接，所以此处将权重上传至 github 仓库
target_uri = 'https://raw.githubusercontent.com/name-used/jassor/refs/heads/master/resources/modnet_photographic_portrait_matting.onnx'


def process(image: np.ndarray, onnx_path: Union[str, Path] = './modnet_human_detect.onnx') -> np.ndarray:
    if not os.path.exists(onnx_path):
        download_checkpoint(onnx_path)
    session = onnxruntime.InferenceSession(onnx_path, None)
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    result = session.run([output_name], {input_name: transpose(image)})
    matte = (np.squeeze(result[0]) * 255).astype('uint8')
    im_h, im_w = image.shape[:2]
    matte = cv2.resize(matte, dsize=(im_w, im_h), interpolation=cv2.INTER_AREA)
    return matte


def transpose(image: np.ndarray):
    # unify image channels to 3
    if len(image.shape) == 2:
        image = image[:, :, None]
    if image.shape[2] == 1:
        image = np.repeat(image, 3, axis=2)
    elif image.shape[2] == 4:
        image = image[:, :, 0:3]

    # normalize values to scale it between -1 to 1
    image = (image - 127.5) / 127.5

    im_h, im_w, im_c = image.shape
    x, y = get_scale_factor(im_h, im_w, ref_size=512)

    # resize image
    image = cv2.resize(image, None, fx=x, fy=y, interpolation=cv2.INTER_AREA)

    # prepare input shape
    image = np.transpose(image)
    image = np.swapaxes(image, 1, 2)
    image = np.expand_dims(image, axis=0).astype('float32')
    return image


# Get x_scale_factor & y_scale_factor to resize image
def get_scale_factor(im_h, im_w, ref_size):

    if max(im_h, im_w) < ref_size or min(im_h, im_w) > ref_size:
        if im_w >= im_h:
            im_rh = ref_size
            im_rw = int(im_w / im_h * ref_size)
        else:
            im_rw = ref_size
            im_rh = int(im_h / im_w * ref_size)
    else:
        im_rh = im_h
        im_rw = im_w

    im_rw = im_rw - im_rw % 32
    im_rh = im_rh - im_rh % 32

    x_scale_factor = im_rw / im_w
    y_scale_factor = im_rh / im_h

    return x_scale_factor, y_scale_factor


def download_checkpoint(path: Union[str, Path]):
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    try:
        sys.stderr.write(f'start download modnet weights from {target_uri}\n')
        sys.stderr.write(f'for more information see https://github.com/ZHKKKe/MODNet\n')
        urllib.request.urlretrieve(target_uri, path)
        sys.stderr.write(f'download success in path {path}\n')
    except Exception as e:
        sys.stderr.write(f'modnet weights download failed, please check network\n')
