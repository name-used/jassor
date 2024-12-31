from jassor.utils import plots
from jassor.components import Masking
import cv2


model_path = rf'..\..\resources\modnet_photographic_portrait_matting.onnx'


# x = cv2.imread('../../resources/test.jpg')
x = cv2.imread('../../resources/trump.jpg')

y = Masking.get_edge(x)
# y = Masking.get_human(model_path, x)

plots([x, y])
