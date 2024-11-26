import cv2
import jassor.utils as J


img = cv2.imread(rf'C:\Users\jizhe\Pictures\test.jpg', cv2.IMREAD_GRAYSCALE)
h, w = img.shape
# 前面是双线性插值，后面是填充所有目标图像素
flags = cv2.INTER_LINEAR | cv2.WARP_FILL_OUTLIERS
# 圆心坐标
# center = (float(img.shape[0] / 2), float(img.shape[1] / 2))
center = (0, 0)
# 圆的半径
maxRadius = (h**2 + w**2) ** 0.5

# linear Polar 极坐标变换, None表示OpenCV根据输入自行决定输出图像尺寸
polar_img = cv2.warpPolar(img, None, center, maxRadius, flags)

J.plots([img, polar_img])
