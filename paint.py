import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QColorDialog,
    QSpinBox, QComboBox, QFileDialog, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QPainter, QPen, QColor, QImage
from PyQt5.QtCore import Qt, QPoint, QRect

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.temp_image = self.image.copy()
        self.drawing = False
        self.start_point = QPoint()
        self.last_point = QPoint()
        self.brush_color = Qt.black
        self.brush_size = 5
        self.brush_shape = 'Düz'
        self.history = []
        self.max_history = 20

    def save_history(self):
        if len(self.history) >= self.max_history:
            self.history.pop(0)
        self.history.append(self.image.copy())

    def undo(self):
        if self.history:
            self.image = self.history.pop()
            self.update()

    def set_brush_color(self, color):
        self.brush_color = color

    def set_brush_size(self, size):
        self.brush_size = size

    def set_brush_shape(self, shape):
        self.brush_shape = shape

    def clear(self):
        self.save_history()
        self.image.fill(Qt.white)
        self.update()

    def resizeEvent(self, event):
        new_image = QImage(self.size(), QImage.Format_RGB32)
        new_image.fill(Qt.white)
        painter = QPainter(new_image)
        painter.drawImage(QPoint(), self.image)
        self.image = new_image
        self.temp_image = self.image.copy()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.save_history()
            self.drawing = True
            self.start_point = event.pos()
            self.last_point = event.pos()
            self.temp_image = self.image.copy()

    def mouseMoveEvent(self, event):
        if not self.drawing:
            return
        painter = QPainter(self.image)
        pen = QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        if self.brush_shape in ['Dümdüz Çizgi', 'Mükemmel Daire', 'Mükemmel Kare', 'Mükemmel Üçgen']:
            self.temp_image = self.image.copy()
            painter_temp = QPainter(self.temp_image)
            painter_temp.setPen(pen)
            dx = event.pos().x() - self.start_point.x()
            dy = event.pos().y() - self.start_point.y()
            if self.brush_shape == 'Dümdüz Çizgi':
                angle = math.degrees(math.atan2(dy, dx))
                angle_rounded = round(angle / 15) * 15
                length = math.hypot(dx, dy)
                rad = math.radians(angle_rounded)
                new_x = self.start_point.x() + length * math.cos(rad)
                new_y = self.start_point.y() + length * math.sin(rad)
                new_point = QPoint(int(new_x), int(new_y))
                painter_temp.drawLine(self.start_point, new_point)
            else:
                rect = self._make_rect(self.start_point, event.pos())
                if self.brush_shape == 'Mükemmel Daire':
                    painter_temp.drawEllipse(rect)
                elif self.brush_shape == 'Mükemmel Kare':
                    painter_temp.drawRect(rect)
                elif self.brush_shape == 'Mükemmel Üçgen':
                    painter_temp.drawPolygon(self._make_triangle(rect))
            self.update()
        else:
            if self.brush_shape == 'Düz':
                painter.drawLine(self.last_point, event.pos())
            elif self.brush_shape == 'Silgi':
                painter.setBrush(Qt.white)
                painter.setPen(Qt.NoPen)
                radius = self.brush_size // 2
                painter.drawEllipse(event.pos(), radius, radius)
            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        painter = QPainter(self.image)
        pen = QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        if self.brush_shape == 'Dümdüz Çizgi':
            dx = event.pos().x() - self.start_point.x()
            dy = event.pos().y() - self.start_point.y()
            angle = math.degrees(math.atan2(dy, dx))
            angle_rounded = round(angle / 15) * 15
            length = math.hypot(dx, dy)
            rad = math.radians(angle_rounded)
            new_x = self.start_point.x() + length * math.cos(rad)
            new_y = self.start_point.y() + length * math.sin(rad)
            new_point = QPoint(int(new_x), int(new_y))
            painter.drawLine(self.start_point, new_point)
        elif self.brush_shape in ['Mükemmel Daire', 'Mükemmel Kare', 'Mükemmel Üçgen']:
            rect = self._make_rect(self.start_point, event.pos())
            if self.brush_shape == 'Mükemmel Daire':
                painter.drawEllipse(rect)
            elif self.brush_shape == 'Mükemmel Kare':
                painter.drawRect(rect)
            elif self.brush_shape == 'Mükemmel Üçgen':
                painter.drawPolygon(self._make_triangle(rect))
        self.drawing = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.drawing and self.brush_shape in ['Dümdüz Çizgi', 'Mükemmel Daire', 'Mükemmel Kare', 'Mükemmel Üçgen']:
            painter.drawImage(self.rect(), self.temp_image, self.temp_image.rect())
        else:
            painter.drawImage(self.rect(), self.image, self.image.rect())

    def _make_rect(self, p1, p2):
        x1, y1 = p1.x(), p1.y()
        x2, y2 = p2.x(), p2.y()
        top_left = QPoint(min(x1, x2), min(y1, y2))
        bottom_right = QPoint(max(x1, x2), max(y1, y2))
        # Mükemmel kare/daire için kare yap
        size = max(bottom_right.x() - top_left.x(), bottom_right.y() - top_left.y())
        return QRect(top_left, top_left + QPoint(size, size))

    def _make_triangle(self, rect):
        from PyQt5.QtGui import QPolygon
        top = QPoint(rect.center().x(), rect.top())
        left = QPoint(rect.left(), rect.bottom())
        right = QPoint(rect.right(), rect.bottom())
        return QPolygon([top, left, right])


class PaintApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint Uygulaması")
        self.setGeometry(100, 100, 800, 600)
        self.canvas = Canvas()

        color_button = QPushButton('Renk Seç')
        color_button.clicked.connect(self.select_color)
        self.brush_size_spin = QSpinBox()
        self.brush_size_spin.setValue(5)
        self.brush_size_spin.setMinimum(1)
        self.brush_size_spin.setMaximum(50)
        self.brush_size_spin.valueChanged.connect(self.change_brush_size)
        clear_button = QPushButton('Temizle')
        clear_button.clicked.connect(self.canvas.clear)
        undo_button = QPushButton('Geri Al')
        undo_button.clicked.connect(self.canvas.undo)
        save_button = QPushButton('Kaydet')
        save_button.clicked.connect(self.save_image)

        self.brush_shape_combo = QComboBox()
        self.brush_shape_combo.addItems(['Düz', 'Dümdüz Çizgi', 'Silgi', 'Mükemmel Daire', 'Mükemmel Kare', 'Mükemmel Üçgen'])
        self.brush_shape_combo.currentTextChanged.connect(self.change_brush_shape)

        h_layout = QHBoxLayout()
        h_layout.addWidget(color_button)
        h_layout.addWidget(self.brush_size_spin)
        h_layout.addWidget(self.brush_shape_combo)
        h_layout.addWidget(clear_button)
        h_layout.addWidget(undo_button)
        h_layout.addWidget(save_button)
        h_layout.addStretch()

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(v_layout)
        self.setCentralWidget(container)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_brush_color(color)

    def change_brush_size(self, value):
        self.canvas.set_brush_size(value)

    def change_brush_shape(self, shape):
        self.canvas.set_brush_shape(shape)

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Resmi Kaydet", "", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)"
        )
        if file_path:
            self.canvas.image.save(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PaintApp()
    window.showMaximized()
    sys.exit(app.exec_())
