import os.path
from typing import Union
from pathlib import Path

import cv2
import numpy as np
import onnxruntime


def inference(onnx_path: Union[str, Path], image: np.ndarray) -> np.ndarray:
    if not os.path.exists(onnx_path):
        download_checkpoint(onnx_path)
    session = onnxruntime.InferenceSession(onnx_path, None)
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    result = session.run([output_name], {input_name: transpose(image)})
    matte = (np.squeeze(result[0]) * 255).astype('uint8')
    im_h, im_w, im_c = image.shape
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
    pass
