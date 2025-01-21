from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QBrush, QColor

class CircleSkeletonWidget(QWidget):
    def __init__(self, parent=None, diameter=20):
        super().__init__(parent)
        self.diameter = diameter
        self.animation_step = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(65)  # Animation speed

    def update_animation(self):
        self.animation_step = (self.animation_step + 5) % 255
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(204, 204, 204, 255 - self.animation_step)  # Gradient effect
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(204, 204, 204, 255 - self.animation_step)  # Gradient effect
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(0, 0, self.width, self.height)

class LoadingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setWindowTitle("Result View")
        # self.setGeometry(100, 100, 800, 400)

        # Main layout for the skeleton loading animation
        # self.central_widget = QWidget(self)
        # self.setCentralWidget(self.central_widget)

        self.setStyleSheet("background-color: rgba(255, 255, 255, 255);")  # Semi-transparent white background
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground,True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setFixedSize(parent.size() if parent else self.size())  # Match parent size

        layout = QVBoxLayout(self)
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
        self.hide()

    def resizeEvent(self, event):
        """Ensure the loading page dynamically resizes with the parent window."""
        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        super().resizeEvent(event)

    def show_loading(self):
        """Show loading screen and update geometry to match parent size."""
        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        self.show()
    
    def show_loading(self):
        self.show()  # Show loading screen

    def hide_loading(self):
        self.hide()  # Hide loading screen

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = QWidget()
    window.resize(800,400)
    window.setStyleSheet("background-color: white;")

    # Add the loading page to the main window
    loading_page = LoadingPage(window)

    # Show the loading screen after a delay (for demo purposes)
    QTimer.singleShot(1000, loading_page.show_loading)  # Show loading after 1 second
    QTimer.singleShot(5000, loading_page.hide_loading)  # Hide loading after 5 seconds

    window.show()
    sys.exit(app.exec())