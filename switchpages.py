import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QSize, Qt

def switch_to_page1(MainWindow):
    try:
        MainWindow.stackedWidget.setCurrentIndex(0)
    except AttributeError:
        print("Error: QStackedWidget not found in MainWindow Instance.")

def switch_to_page2(MainWindow):
    try:
        MainWindow.stackedWidget.setCurrentIndex(1)
    except AttributeError:
        print("Error: QSTackedWidget not found in MainWindow Instance")

def switch_to_page3(MainWindow):
    try:
        MainWindow.stackedWidget.setCurrentIndex(2)
    except AttributeError:
        print("Error: QStackedWidget not found in MainWindow Instance.")