import numpy as np
import cv2
import jassor.utils as J


def main():
    # 这个方法非常简单，就是用来做图像采样的
    for T_len in range(30, 38):
        # 输出元素满足的几个性质：总是从 0 开始, 最后一个数字 + 5 == T_len, 间隔大致是 3（只会更短不会更长）
        print(J.uniform_iter(T_len, 5, 3))
    # 现在让我们把它画在图上吧：
    temp = np.zeros((300, 315, 3), dtype=np.uint8)
    grids = [(x, y) for x in J.uniform_iter(315, 51, 45) for y in J.uniform_iter(300, 51, 45)]
    colors = J.random_colors(len(grids))
    for (x, y), color in zip(grids, colors):
        cv2.circle(temp, (x+25, y+25), 25, color=color)
    J.plot(temp)


if __name__ == '__main__':
    main()
