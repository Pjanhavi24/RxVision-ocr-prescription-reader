from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QBrush, QColor

class CircleSkeletonWidget(QLabel):
    def __init__(self, parent=None, diameter=20):
        super().__init__(parent)
        self.diameter = diameter
        self.animation_step = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)  # Animation speed

    def update_animation(self):
        self.animation_step = (self.animation_step + 5) % 255
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(204, 204, 204, 255 - self.animation_step)  # Gradient effect
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, self.diameter, self.diameter)

class LineSkeletonWidget(QLabel):
    def __init__(self, parent=None, width=200, height=20):
        super().__init__(parent)
        self.width = width
        self.height = height
        self.animation_step = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50)  # Animation speed

    def update_animation(self):
        self.animation_step = (self.animation_step + 5) % 255
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(204, 204, 204, 255 - self.animation_step)  # Gradient effect
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(0, 0, self.width, self.height)

class LoadingPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Result View")
        self.setGeometry(100, 100, 800, 400)

        # Main layout for the skeleton loading animation
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # Create rows with a circle and line for the skeleton loader
        for _ in range(3):  # Three rows
            row_layout = QHBoxLayout()
            circle = CircleSkeletonWidget(self, diameter=20)
            circle.setFixedSize(20, 20)
            line = LineSkeletonWidget(self, width=300, height=20)
            line.setFixedSize(300, 20)
            row_layout.addWidget(circle)
            row_layout.addSpacing(10)
            row_layout.addWidget(line)
            row_layout.addStretch()
            layout.addLayout(row_layout)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LoadingPage()
    window.show()
    sys.exit(app.exec_())
