import os.path
import sys
import PIL.Image
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QWidget, QCheckBox, QSlider
)
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QPoint, QSize


def main():
    app = QApplication(sys.argv)
    editor = ImageLogoEditor()
    editor.show()
    sys.exit(app.exec_())


class ImageLogoEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        screen = QApplication.primaryScreen()  # 获取主屏幕
        screen_size = screen.geometry()  # 获取屏幕的大小
        self.W = screen_size.width() - 100
        self.H = screen_size.height() - 200
        self.setGeometry(0, 0, self.W, self.H)

        # 图片大小
        self.w = 800
        self.h = 800

        # Initialize images
        self.image = None
        self.logo = None
        self.canvas = QImage(QSize(self.w, self.h), QImage.Format_RGB888)
        self.canvas.fill(Qt.white)
        self.temp = QImage(QSize(self.w, self.h), QImage.Format_RGBA8888)
        self.display_logo = True

        # Drawing variables
        self.drawing = False
        self.last_point = QPoint()
        self.text_mode = False
        self.text_size = 20

        # Main layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Image label
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(self.w, self.h)
        self.image_label.setStyleSheet("background-color: lightgray;")
        layout.addWidget(self.image_label)

        # Controls layout
        controls_layout = QHBoxLayout()
        layout.addLayout(controls_layout)

        # Buttons and checkbox
        load_image_btn = QPushButton("Load Image")
        load_image_btn.clicked.connect(self.load_image)
        controls_layout.addWidget(load_image_btn)

        load_logo_btn = QPushButton("Load Logo")
        load_logo_btn.clicked.connect(self.load_logo)
        controls_layout.addWidget(load_logo_btn)

        load_image_btn = QPushButton("Load Image Logo")
        load_image_btn.clicked.connect(self.load_image_logo)
        controls_layout.addWidget(load_image_btn)

        clear_logo_btn = QPushButton("Clear Logo")
        clear_logo_btn.clicked.connect(self.clear_logo)
        controls_layout.addWidget(clear_logo_btn)

        reset_drawing_btn = QPushButton("Reset Drawing")
        reset_drawing_btn.clicked.connect(self.reset_drawing)
        controls_layout.addWidget(reset_drawing_btn)

        save_images_btn = QPushButton("Save Marked Image")
        save_images_btn.clicked.connect(self.save_images)
        controls_layout.addWidget(save_images_btn)

        save_logo_btn = QPushButton("Save Logo")
        save_logo_btn.clicked.connect(self.save_logo)
        controls_layout.addWidget(save_logo_btn)

        self.logo_checkbox = QCheckBox("Display Logo")
        self.logo_checkbox.stateChanged.connect(self.toggle_logo_display)
        controls_layout.addWidget(self.logo_checkbox)

        text_size_label = QLabel("Text Size:")
        controls_layout.addWidget(text_size_label)

        self.text_size_slider = QSlider(Qt.Horizontal)
        self.text_size_slider.setRange(10, 50)
        self.text_size_slider.setValue(self.text_size)
        self.text_size_slider.valueChanged.connect(self.change_text_size)
        controls_layout.addWidget(self.text_size_slider)

        self.image_label.mousePressEvent = self.mouse_press
        self.image_label.mouseMoveEvent = self.mouse_move
        self.image_label.mouseReleaseEvent = self.mouse_release
        self.image_label.keyPressEvent = self.key_press

        self.reset_drawing()
        self.logo_checkbox.setChecked(True)
        if os.path.exists('./image_path.txt'):
            with open('./image_path.txt') as f:
                file_path = f.readlines()[0]
            self.load_image(file_path)
        if os.path.exists('./logo.png'):
            self.load_logo('./logo.png')

    def load_image(self, file_path: str = None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
            with open('./image_path.txt', 'w') as f:
                f.write(file_path)
        if file_path:
            self.image = QImage(file_path)
            self.update_display()
            self.w, self.h = limit_wh(self.image.width(), self.image.height(), self.W, self.H)
            self.resize_contents()

    def load_logo(self, file_path: str = None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Logo File", "", "Images (*.png *.jpg *.bmp)")
        if file_path:
            # self.logo = QImage(file_path).convertToFormat(QImage.Format_Grayscale8)
            self.logo = image2logo(QImage(file_path), 128)
            self.update_display()

    def clear_logo(self):
        self.logo = None
        self.update_display()

    def reset_drawing(self):
        # self.temp.fill(QColor(0, 0, 0, 0))
        self.temp.fill(QColor(255, 255, 255, 0))
        self.update_display()

    def save_images(self):
        image_temp = QImage(self.canvas)
        painter = QPainter(image_temp)
        painter.setOpacity(1)
        if self.image:
            painter.drawImage(0, 0, self.image.scaled(image_temp.size(), Qt.IgnoreAspectRatio))
        painter.end()

        logo_temp = QImage(self.canvas)
        painter = QPainter(logo_temp)
        painter.setOpacity(1)
        if self.logo:
            painter.drawImage(0, 0, self.logo.scaled(logo_temp.size(), Qt.IgnoreAspectRatio))
        painter.drawImage(0, 0, self.temp)
        painter.end()

        # self.image.save("image_output.png")
        file_path, _ = QFileDialog.getSaveFileName(self, "Open Logo File", "image_logo.png", "Images (*.png *.jpg *.bmp)")
        if file_path:
            set_logo(image_temp, logo_temp, file_path)

    def save_logo(self):
        logo_temp = QImage(self.canvas)
        painter = QPainter(logo_temp)
        painter.setOpacity(1)
        if self.logo:
            painter.drawImage(0, 0, self.logo.scaled(logo_temp.size(), Qt.IgnoreAspectRatio))
        painter.drawImage(0, 0, self.temp)
        painter.end()
        # self.image.save("image_output.png")
        file_path, _ = QFileDialog.getSaveFileName(self, "Open Logo File", "logo.png", "Images (*.png *.jpg *.bmp)")
        if file_path:
            logo_temp.save(file_path)

    def load_image_logo(self, file_path: str = None):
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open Logo File", "", "Images (*.png *.jpg *.bmp)")
        if file_path:
            # self.logo = QImage(file_path).convertToFormat(QImage.Format_Grayscale8)
            self.image, self.logo = from_image_logo(file_path)
            self.update_display()

    def toggle_logo_display(self):
        self.display_logo = self.logo_checkbox.isChecked()
        self.update_display()

    def change_text_size(self, value):
        self.text_size = value

    def update_display(self):
        display = QImage(self.canvas)
        painter = QPainter(display)
        painter.setOpacity(1)
        if self.image:
            painter.drawImage(0, 0, self.image.scaled(display.size(), Qt.IgnoreAspectRatio))
        if self.display_logo and self.logo:
            painter.drawImage(0, 0, self.logo.scaled(display.size(), Qt.IgnoreAspectRatio))
        painter.drawImage(0, 0, self.temp)
        painter.end()

        self.image_label.setPixmap(QPixmap.fromImage(display).scaled(self.image_label.size(), Qt.KeepAspectRatio))

    def mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
            painter = QPainter(self.temp)
            pen = QPen(Qt.black, 5, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawPoint(self.last_point)
            painter.end()
            self.update_display()

    def mouse_move(self, event):
        if self.drawing:
            painter = QPainter(self.temp)
            pen = QPen(Qt.black, 5, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            painter.end()
            self.last_point = event.pos()
            self.update_display()

    def mouse_release(self, event):
        self.drawing = False

    def key_press(self, event):
        if event.key() == Qt.Key_T:
            self.text_mode = not self.text_mode

    def resize_contents(self):
        self.canvas = QImage(QSize(self.w, self.h), QImage.Format_RGB888)
        self.canvas.fill(Qt.white)
        new_temp = QImage(QSize(self.w, self.h), QImage.Format_RGBA8888)
        painter = QPainter(new_temp)
        painter.drawImage(0, 0, self.temp.scaled(QSize(self.w, self.h), Qt.IgnoreAspectRatio))
        self.temp = new_temp
        self.image_label.setFixedSize(self.w, self.h)
        self.update_display()


def image2logo(image: QImage, thresh: int):
    w, h = image.width(), image.height()
    data = image.convertToFormat(QImage.Format_Grayscale8)
    ptr = data.bits()
    ptr.setsize(data.byteCount())
    data = np.array(ptr).reshape(h, w).copy()
    new_data = np.zeros((h, w, 4), dtype=np.uint8)
    new_data[data <= thresh, 3] = 255
    new_data[data > thresh, 3] = 0
    new_image = QImage(new_data.data, w, h, w * 4, QImage.Format_RGBA8888)
    return new_image


def set_logo(image: QImage, logo: QImage, output_path: str):
    w, h = image.width(), image.height()
    image = image.convertToFormat(QImage.Format_RGB888)
    ptr = image.bits()
    ptr.setsize(image.byteCount())
    image = np.array(ptr).reshape((h, w, 3)).copy()

    # logo = logo.convertToFormat(QImage.Format_Grayscale8)
    ptr = logo.bits()
    ptr.setsize(logo.byteCount())
    logo = np.array(ptr).reshape((h, w, 3)).copy()

    logo_image = (image >> 1 << 1) + logo[..., 0:1].astype(bool)

    PIL.Image.fromarray(logo_image).save(output_path)


def from_image_logo(input_path: str):
    image_logo = PIL.Image.open(input_path)
    image_logo = np.asarray(image_logo)
    h, w, _ = image_logo.shape

    image = image_logo

    logo_value = image_logo % 2
    logo_value = logo_value.sum(axis=2) > 1
    logo = np.zeros((h, w, 4), dtype=np.uint8)
    logo[..., 3] = (1 - logo_value) * 255

    image = QImage(image.data, w, h, w * 3, QImage.Format_RGB888)
    logo = QImage(logo.data, w, h, w * 4, QImage.Format_RGBA8888)
    return image, logo


def limit_wh(w, h, max_w, max_h):
    if w <= max_w and h <= max_h:
        return w, h
    if w > max_w:
        # w / max_w == h / h'
        h = h * max_w / w
        w = max_w
    if h > max_h:
        w = w * max_h / h
        h = max_h
    return int(w), int(h)
