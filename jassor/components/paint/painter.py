from typing import List
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QShortcut, QFileDialog
from PyQt5.QtGui import QKeySequence, QMouseEvent, QWheelEvent, QPixmap
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor


class JassorWindow(QWidget):
    def __init__(self, win_width=800, win_height=400, click_delay=200, move_threshold=5):
        super().__init__()
        self.setWindowTitle("鼠标 + 键盘事件处理示例")
        self.resize(win_width, win_height)

        self.layout = QVBoxLayout()
        self.canvas = JassorCanvas()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        # 鼠标事件控制
        self.setMouseTracking(True)
        self.left_pressed = False
        self.right_pressed = False
        self.dragging = False
        self.active_button = None  # 'left' or 'right'
        self.press_pos = None
        self._left_click_event = None

        self.click_timer = QTimer(self)
        self.click_timer.setSingleShot(True)
        self.click_timer.timeout.connect(self._emit_left_single_click)
        self.click_delay = click_delay  # ms
        self.move_threshold = move_threshold  # px
        self.move_point_list = []

    # 事件回调函数，按需实现
    def on_left_click(self, event: QMouseEvent):
        raise NotImplementedError

    def on_left_double_click(self, event: QMouseEvent):
        raise NotImplementedError

    def on_left_drag(self, start_point: QPoint, end_event: QMouseEvent, move_point_list: List[QPoint]):
        raise NotImplementedError

    def on_right_click(self, event: QMouseEvent):
        raise NotImplementedError

    def on_right_drag(self, start_point: QPoint, end_event: QMouseEvent, move_point_list: List[QPoint]):
        raise NotImplementedError

    def on_wheel(self, event: QWheelEvent):
        raise NotImplementedError

    # 按钮定义
    def add_button(self, name: str, shortcut: str, callback: callable):
        button = QPushButton(f"{name} ({shortcut})")
        button.clicked.connect(callback)
        self.layout.addWidget(button)
        if shortcut:
            shortcut = QShortcut(QKeySequence(shortcut), self)
            shortcut.activated.connect(callback)

    # -------------------------------
    # 鼠标事件封装(单击、双击、拖拽)
    # -------------------------------
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._interrupt_event("right")  # cancel any right-button action
            self.left_pressed = True
            self.active_button = "left"
        elif event.button() == Qt.RightButton:
            self._interrupt_event("left")   # cancel any left-button action
            self.right_pressed = True
            self.active_button = "right"

        self.press_pos = event.pos()
        self.dragging = False

    def mouseMoveEvent(self, event: QMouseEvent):
        if not self.press_pos:
            return
        if self.dragging:
            self.move_point_list.append(event.pos())
            return
        if (event.pos() - self.press_pos).manhattanLength() > self.move_threshold:
            if self.active_button:
                self.dragging = True
                self.move_point_list.clear()
                self.move_point_list.append(self.press_pos)
                self.move_point_list.append(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent):
        # 记录当前行为是哪只键
        if self.active_button == "left" and event.button() == Qt.LeftButton:
            if self.dragging:
                self.on_left_drag(self.press_pos, event, self.move_point_list)
            elif (event.pos() - self.press_pos).manhattanLength() > self.move_threshold:
                # 除拖拽外，任何 click 都必须原地进行
                self._reset_state()
            elif self.click_timer.isActive():
                self.click_timer.stop()
                self.on_left_double_click(event)
            else:
                self._left_click_event = event
                self.click_timer.start(self.click_delay)
        elif self.active_button == "right" and event.button() == Qt.RightButton:
            if self.dragging:
                self.on_right_drag(self.press_pos, event, self.move_point_list)
            elif (event.pos() - self.press_pos).manhattanLength() > self.move_threshold:
                # 除拖拽外，任何 click 都必须原地进行
                self._reset_state()
            else:
                self.on_right_click(event)

    def wheelEvent(self, event: QWheelEvent):
        self.on_wheel(event)
        self._reset_state()

    def _emit_left_single_click(self):
        if self.left_pressed and not self.dragging:
            self.on_left_click(self._left_click_event)
        self._reset_state()

    def _interrupt_event(self, button):
        if button == "left" and self.left_pressed:
            print("[中断] 左键事件被右键打断")
        elif button == "right" and self.right_pressed:
            print("[中断] 右键事件被左键打断")
        self._reset_state()

    def _reset_state(self):
        self.left_pressed = False
        self.right_pressed = False
        self.dragging = False
        self.active_button = None
        self.press_pos = None
        self._left_click_event = None


class JassorCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None  # 存储背景图片
        self.lines = []  # 存储所有线条 (color, points)
        self.texts = []  # 存储当前显示的文本

    def paintEvent(self, event):
        painter = QPainter(self)

        # 绘制背景图片（如果有）
        if self.image:
            painter.drawPixmap(self.rect(), self.image)
        else:
            painter.fillRect(self.rect(), Qt.white)

        # 绘制所有存储的线条
        for color, points in self.lines:
            pen = QPen(QColor(color), 2)
            painter.setPen(pen)
            for i in range(1, len(points)):
                painter.drawLine(points[i - 1], points[i])

        # 绘制文本
        for color, (x, y), text in self.texts:
            painter.setPen(QPen(QColor(color), 2))
            painter.drawText(x, y, text)


class DemoWindow(JassorWindow):
    def __init__(self):
        super(DemoWindow, self).__init__()
        self.add_button('load image', 'ctrl+d', self.load_image)

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择图片文件', '',
            '图像文件 (*.png *.jpg *.jpeg *.bmp *.gif)'
        )
        if file_path:
            self.canvas.image = QPixmap(file_path)
            self.canvas.update()

    def on_left_click(self, event: QMouseEvent):
        x, y = event.pos().x(), event.pos().y()
        self.canvas.texts.append(('black', (x, y), f'left_click: {x, y}'))
        self.canvas.update()

    def on_left_double_click(self, event: QMouseEvent):
        x, y = event.pos().x(), event.pos().y()
        self.canvas.texts.append(('black', (x, y), f'left_double_click: {x, y}'))
        self.canvas.update()

    def on_left_drag(self, start_point: QPoint, end_event: QMouseEvent, move_point_list: List[QPoint]):
        self.canvas.lines.append(('red', move_point_list[:]))
        x, y = start_point.x(), start_point.y()
        self.canvas.texts.append(('black', (x, y), f'left_drag: {x, y}'))
        self.canvas.update()

    def on_right_click(self, event: QMouseEvent):
        x, y = event.pos().x(), event.pos().y()
        self.canvas.texts.append(('black', (x, y), f'right_click: {x, y}'))
        self.canvas.update()

    def on_right_drag(self, start_point: QPoint, end_event: QMouseEvent, move_point_list: List[QPoint]):
        self.canvas.lines.append(('green', move_point_list[:]))
        x, y = start_point.x(), start_point.y()
        self.canvas.texts.append(('black', (x, y), f'right_drag: {x, y}'))
        self.canvas.update()

    def on_wheel(self, event: QWheelEvent):
        x, y = event.pos().x(), event.pos().y()
        self.canvas.texts.append(('black', (x, y), f'wheel: delta {event.angleDelta().y()}'))
        self.canvas.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DemoWindow()
    win.show()
    sys.exit(app.exec_())
