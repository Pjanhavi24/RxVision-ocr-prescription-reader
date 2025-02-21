# -*- coding: utf-8 -*-

import sys
import ctypes
import cv2
from open_file_dialog import open_file_dialog
from api_handler import get_medicine_data
from check_internet import *
from switchpages import *
from crop import open_crop_window
from loading import LoadingPage
from process_and_extract import *
from process_and_extract import processAndExtract
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import (QCoreApplication,QThread,QUrl, QDate, QDateTime, QLocale, QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QTimer, pyqtSignal)
from PyQt6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,QMovie, QFont, QFontDatabase, QGradient, QIcon, QImage, QKeySequence, QLinearGradient, QPainter, QPalette, QPixmap, QRadialGradient, QTransform)
from PyQt6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QSizePolicy, QSpacerItem, QStackedWidget, QTextEdit,QScrollArea, QVBoxLayout, QWidget, QGraphicsDropShadowEffect,QMessageBox)

#Class to make the label Clickable like a button to call the API
class clickableLabel(QLabel):

    #customise signal to emit when label is clicked
    label_clicked_signal=pyqtSignal(dict)

    def __init__(self,text, parent=None):
        super().__init__(text,parent)
        self.setStyleSheet("text-align: left; padding: 5px; font-size: 14px; cursor: pointer;")
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.label_clicked()

    def label_clicked(self):
        # Emit the signal with the associated data
        if self.data:
            self.label_clicked_signal.emit(self.data)

class ProcessWorker(QThread):
    processing_done= pyqtSignal(list) # Signal to send the result back to the main thread
    processing_error= pyqtSignal(str) # Signal to handle error

    def __init__(self, image_path):
         super().__init__()
         self.image_path=image_path

    def run(self):
        try:
            # Call the external function to process the image and extract text
            extracted_text= processAndExtract(self.image_path)
            # If the extracted text is a list, send it directly
            if isinstance(extracted_text, list):
                self.processing_done.emit(extracted_text)
            else:
                self.processing_done.emit(extracted_text.split('\n'))
        except Exception as e:
            self.processing_error.emit(str(e))

class Ui_MainWindow(object):
    def call_switch_to_page1(self):
        switch_to_page1(self)  # Pass the MainWindow instance to the function

    def call_switch_to_page2(self):
        switch_to_page2(self)  # Pass the MainWindow instance to the function 

    def call_switch_to_page3(self):
        switch_to_page3(self)  #Pass the MainWindow instance to the function
    
    def apply_theme(self):
        #detect the systems base color
        appPalette=QApplication.palette()
        base_color=appPalette.color(QPalette.ColorRole.Window)
        is_darkmode=base_color.lightness() < 128

        # Debugging Output
        print(f"Detected base color: {base_color.name()}, Dark Mode: {is_darkmode}")
 
        if is_darkmode:
            #Dark mode Theme
            self.setStyleSheet("""QWidget#MainWindow {background-color: #2B2B2B;}
                                  QLabel#page_3 {color:#000000}
                                  QLabel#medicine_name {color:#000000}
                                  QLabel#name_heading {color:#000000}
                                  QLabel#composition_label {color:#000000}
                                  QLabel#manufacture_label {color:#000000}
                                  QLabel#description_label {color:#000000}
                               """)             
        else:
            self.setStyleSheet("""
            QWidget#MainWindow {
                background-color: #F5F5F5;
            }
        """)

    def on_processing_done(self,medicine_names):
        # Populate medicine labels in the left layout (page 3)
        self.populate_medicine_labels(medicine_names)

        # Close the loading page
        self.loading_page.hide()

        # Switch to page 3 to show the extracted text
        self.stackedWidget.setCurrentIndex(2)

        #clean up the worker
        self.worker.deleteLater()

    def on_processing_error(self,error_message):
        # Display the error message
        QMessageBox.critical(None, "Error", f"An error occurred: {error_message}")

        # Close the loading page
        self.loading_page.hide()

        #clean up the worker
        self.worker.deleteLater()


    def confirm_selection(self):
        try:
            self.loading_page.show_loading()
            
            # Check internet connectivity
            if not check_internet_connection():
                QMessageBox.warning(None, "Internet Connection Error", "No internet connection. Please check your network and try again.")
                self.loading_page.hide()
                return
            
            #Ensure that an image has been selected
            if hasattr(self, 'selected_image_path') and self.selected_image_path:
                # Get the image path selected in the file picker
                image_path = self.selected_image_path #This should be set during Image Selection


                # #Call the external Function to process the image and extract text
                # extracted_text = processAndExtract(image_path)

                # Create a worker thread
                self.worker = ProcessWorker(image_path)
                self.worker.processing_done.connect(self.on_processing_done)
                self.worker.processing_error.connect(self.on_processing_error)

                # Start the worker thread
                self.worker.start()

            else:
            # Handle the case where no image was selected (optional)
                QMessageBox.warning(self, "No Image Selected", "Please select an image first.")  
                self.loading_page.hide()
        except Exception as e:
            # Catch all other unexpected errors and display an error message
            QMessageBox.critical(None, "Error", f"An unexpected error occurred: {str(e)}")
            self.loading_page.hide()

    def show_copied_popup(self):
        # Create the label for the popups
        self.copied_label = QLabel("Text Copied", self)
        self.copied_label.setStyleSheet("background-color: None; color: black; font-size: 14px; padding: 5px;")
        self.copied_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Position the label near the home button
        self.copied_label.move(self.back_pushbutton.x() + self.back_pushbutton.width(), self.back_pushbutton.y())
        
        # Show the label and set a timer to hide it after 2 seconds
        self.copied_label.show()
        QTimer.singleShot(2000, self.copied_label.hide)  # Hide after 2 seconds

    def copy_text(self):

        #get text from the Qtextedit
        text = self.display_textedit.toPlainText()

        #Access the clipboard
        clipboard= QApplication.clipboard()
        clipboard.setText(text)

        self.show_copied_popup()


    def open_crop_window(self):
        if hasattr(self, 'selected_image_path') and self.selected_image_path:
                # Call the crop window and get the cropped image path
            cropped_image_path = open_crop_window(self.selected_image_path,medicine_dataset)

            if cropped_image_path:
                # Load the cropped image from file into a QPixmap
                cropped_image = QPixmap(cropped_image_path)  # Convert the file path to QPixmap

                # Display the cropped image in the QLabel
                self.preview_image_label.setPixmap(cropped_image)  # Update QLabel with QPixmap
                self.preview_image_label.setScaledContents(True)
                self.preview_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                extrated_text_cropped= processAndExtract(cropped_image_path)

                # Pass the cropped image to the populate_medicine function
                self.populate_medicine_labels(extrated_text_cropped)

                self.stackedWidget.setCurrentIndex(2)
            else:
                print("Cropping was canceled or failed.")
        else:
                # Handle the case where no image was selected
            QMessageBox.warning(self, "No Image Selected", "Please select an image first.")

    def update_right_panel(self, data):
        #Update Name
        self.name_label.setText(data.get("name", "Name not available"))
        self.name_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        #Update composition
        self.Composition_label.setText(f"Composition: {data.get('composition1', ' Not Available')}")
        self.Composition_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        # Update Manufacturer
        self.manufacturer_label.setText(f"Manufacturer: {data.get('manufacturer_name', ' Not Available')}")
        self.manufacturer_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        # Update Description
        usage_info = data.get("usage1", "\nNo description available.")
        # Format the usage description (if it's a list, convert to a string)
        if isinstance(usage_info, list):
            usage_info = "\n".join(usage_info)
        self.description_widget.setText(f"Description:\n{usage_info}")
        self.description_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    def fetch_medicine_data(self,medicine_name):
        """
    Fetches data for the selected medicine using the API and updates the right panel.
    Args:
        medicine_name (str): The name of the selected medicine.
    """
        try:
            data=get_medicine_data(medicine_name)
            # Ensure data is a non-empty list
            if isinstance(data, list) and len(data) > 0:
                medicine_info=data[0] # Get the first item from the list
            else:
                medicine_info= {"name": "Unknown", "details":"No details available"}
            self.update_right_panel(medicine_info)
        except Exception as e:
            print(f"Error fetching medicine data")
    
    #methods to update, render and close the frame of the main screen bgvideo
    def update_frame(self):
            width=self.width()
            height=self.height()
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES,0) #restarts the video when it ends
                return
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            q_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.home_animation.setPixmap(QPixmap.fromImage(q_image))
            self.home_animation.setGeometry(0,0,width,height)

    def on_resize(self,event):
        """Resize video to fit the entire screen."""
        self.background_video.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def closeEvent(self, event):
        self.cap.release()
        event.accept() #Accept the close event

    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(865, 697)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)        
        MainWindow.setStyleSheet(u"QMainWindow{\n"
"background-color: #FFFFFF\n"
"}")
        # self.display_textedit=QTextEdit(self)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"")
        self.verticalLayout_4 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_1 = QWidget()
        self.page_1.setObjectName(u"page_1")
        self.verticalLayout_3 = QVBoxLayout(self.page_1)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(1)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(-1, -1, -1, 10)
        self.mainHeading_1 = QLabel(self.page_1)
        self.mainHeading_1.setObjectName(u"mainHeading_1")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.mainHeading_1.sizePolicy().hasHeightForWidth())
        self.mainHeading_1.setSizePolicy(sizePolicy1)
        font = QFont()
        font.setFamilies([u"Berlin Sans FB Demi"])
        font.setPointSize(33)
        font.setBold(True)
        font.setItalic(False)
        self.mainHeading_1.setFont(font)
        self.mainHeading_1.setStyleSheet(u"QLabel{\n"
"color:#6B7075\n"
"}")
        self.mainHeading_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mainHeading_1.setMargin(0)

        self.verticalLayout_2.addWidget(self.mainHeading_1)

        self.tagline = QLabel(self.page_1)
        self.tagline.setObjectName(u"tagline")
        sizePolicy1.setHeightForWidth(self.tagline.sizePolicy().hasHeightForWidth())
        self.tagline.setSizePolicy(sizePolicy1)
        font1 = QFont()
        font1.setPointSize(11)
        font1.setBold(False)
        font1.setItalic(True)
        self.tagline.setFont(font1)
        self.tagline.setStyleSheet(u"QLabel{\n"
"color:#6B7075\n"
"}")
        self.tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.tagline)

        self.line_3 = QFrame(self.page_1)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_3)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")

        self.verticalLayout_2.addLayout(self.horizontalLayout_7)

        self.home_animation= QLabel(self.page_1)
        self.home_animation.setObjectName(u"home_screen_animation")
        self.home_animation.setGeometry(0,0,self.width(),self.height())
        self.home_animation.setScaledContents(True)
        self.home_animation.lower()
        #load the video
        self.cap= cv2.VideoCapture("resource/homepageanimation2.mp4")
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        
        #Initialize the Stacked widget with pages
        self.stackedWidget= QStackedWidget(self)

        self.pick_image_pushbutton = QPushButton(self.page_1)
        self.pick_image_pushbutton.setObjectName(u"pick_image_pushbutton")
        self.pick_image_pushbutton.clicked.connect(lambda: open_file_dialog(self))
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.pick_image_pushbutton.sizePolicy().hasHeightForWidth())
        self.pick_image_pushbutton.setSizePolicy(sizePolicy3)
        self.pick_image_pushbutton.setMinimumSize(QSize(40, 30))
        self.pick_image_pushbutton.setMaximumSize(QSize(170, 90))
        font2 = QFont()
        font2.setFamilies([u"Calibri"])
        font2.setPointSize(12)
        font2.setBold(True)
        self.pick_image_pushbutton.setFont(font2)
        self.pick_image_pushbutton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pick_image_pushbutton.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.pick_image_pushbutton.setStyleSheet(u"QPushButton\n"
"{\n"
"color:#ffffff;\n"
"background-color:#9c9c9c;\n"
"border-radius:9;\n"
"transition: background-color 0.5s ease-in-out, \n"
"                color 0.5s ease-in-out, \n"
"                padding 0.2s ease-in-out, \n"
"border:1px solid #cccccc;\n"
"}\n"
"QPushButton:hover\n"
"{\n"
"color:#111111;\n"
"background-color:#ffffff;\n"
"transition: background-color 1s ease-in-out, \n"
"            color 1s ease-in-out, \n"
"            padding 0.2s ease-in-out, \n"
"border:1px solid #cccccc\n"
"}\n"
"QPushButton:pressed {\n"
"    background-color: #38454C;  /* Darker background when pressed */\n"
"    padding-top: 5px;  /* Slightly decrease padding for pressed effect */\n"
"    padding-left: 10px;  /* Slightly decrease padding for pressed effect */\n"
"}")

        self.horizontalLayout_2.addWidget(self.pick_image_pushbutton)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)

        self.line_4 = QFrame(self.page_1)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_2.addWidget(self.line_4)

        self.label_3 = QLabel(self.page_1)
        self.label_3.setObjectName(u"label_3")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy4)
        self.label_3.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.label_3)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        self.stackedWidget.addWidget(self.page_1)

        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.verticalLayout_5 = QVBoxLayout(self.page_2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(40, 20, 40, 20)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(-1, -1, -1, 20)
        self.label_2 = QLabel(self.page_2)
        self.label_2.setObjectName(u"label_2")
        sizePolicy3.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy3)
        self.label_2.setMaximumSize(QSize(40, 40))
        self.label_2.setStyleSheet(u"QLabel{\n"
"color:#FFFFFF\n"
"}")
        self.label_2.setPixmap(QPixmap(u"resource/fileicon.png"))
        self.label_2.setScaledContents(True)

        self.horizontalLayout_4.addWidget(self.label_2)

        self.label = QLabel(self.page_2)
        self.label.setObjectName(u"label")
        font3 = QFont()
        font3.setFamilies([u"Berlin Sans FB Demi"])
        font3.setPointSize(20)
        font3.setBold(True)
        self.label.setFont(font3)
        self.label.setStyleSheet(u"QLabel{\n"
"color:#6B7075\n"
"}")

        self.horizontalLayout_4.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.widget = QWidget(self.page_2)
        self.widget.setObjectName(u"widget")
        self.widget.setStyleSheet(u"QWidget {\n"
"    background-color: #e6f7ff;  /* Light blue color */\n"
"    border-bottom: 1px solid #b3d7ff;  /* Optional border for separation */\n"
"}\n"
"")

        self.horizontalLayout_4.addWidget(self.widget)

        self.home1_pushbutton = QPushButton(self.page_2)
        self.home1_pushbutton.setObjectName(u"home1_pushbutton")
        self.home1_pushbutton.setFont(font2)
        self.home1_pushbutton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.home1_pushbutton.setStyleSheet(u"QPushButton {\n"
"    background-color: #9c9c9c;  /* Default button color */\n"
"    color: white;\n"
"    border-radius: 10px;\n"    
"    padding: 8px;\n"
"}\n"
"\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(255, 255, 255, 0.3);  /* Soft white glow */\n"
"    color: #000000;\n"
"    border: 1px solid #cccccc;\n"
"}")  

        self.home1_pushbutton.clicked.connect(self.call_switch_to_page1)
        

        self.horizontalLayout_4.addWidget(self.home1_pushbutton)
        self.extractedText_pushbutton = QPushButton(self.page_2)
        self.extractedText_pushbutton.setObjectName(u"extractedText_pushbutton")
        self.extractedText_pushbutton.setFont(font2)
        self.extractedText_pushbutton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.extractedText_pushbutton.setStyleSheet(u"QPushButton {\n"
"    background-color: #9c9c9c;  /* Default button color */\n"
"    color: white;\n"
"    border-radius: 10px;\n"
"    padding: 8px;\n"
"}\n"
"\n"
"\n"
"QPushButton:hover {\n"
"    background-color: rgba(255, 255, 255, 0.3);  /* Soft white glow */\n"
"    color: #000000;\n"
"    border: 1px solid #cccccc;\n"
"}")

        self.extractedText_pushbutton.clicked.connect(self.call_switch_to_page3)
        self.horizontalLayout_4.addWidget(self.extractedText_pushbutton)


        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.line = QFrame(self.page_2)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.crop_pushbutton = QPushButton(self.page_2)
        self.crop_pushbutton.setObjectName(u"crop_pushbutton")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.crop_pushbutton.sizePolicy().hasHeightForWidth())
        self.crop_pushbutton.setSizePolicy(sizePolicy5)
        self.crop_pushbutton.setMinimumSize(QSize(0, 16))
        self.crop_pushbutton.setMaximumSize(QSize(16777215, 30))
        font4 = QFont()
        font4.setFamilies([u"Bahnschrift SemiCondensed"])
        font4.setPointSize(12)
        self.crop_pushbutton.setFont(font4)
        self.crop_pushbutton.setStyleSheet(u"")
        icon = QIcon()
        icon.addFile(u"resource/crop.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.crop_pushbutton.setIcon(icon)
        self.crop_pushbutton.setIconSize(QSize(18, 18))
        self.crop_pushbutton.clicked.connect(self.open_crop_window)

        self.verticalLayout.addWidget(self.crop_pushbutton)

        self.preview_frame = QFrame(self.page_2)
        self.preview_frame.setObjectName(u"preview_frame")
        # sizePolicy2.setHeightForWidth(self.preview_frame.sizePolicy().hasHeightForWidth())
        self.preview_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_frame.setStyleSheet(u"QFrame {\n"
"    background: qlineargradient(\n"
"        x1: 0, y1: 0, x2: 1, y2: 1,\n"
"        stop: 0 #c0c0c0,\n"
"        stop: 1 #e0e0e0\n"
"    );\n"
"	border:2px black;\n"
"    border-radius: 10px;\n"
"}\n"
"")
        self.preview_layout= QVBoxLayout(self.preview_frame)
        # Add QLabel to preview_frame
        self.preview_image_label = QLabel(self.preview_frame)
        self.preview_image_label.setObjectName("image_label")
        self.preview_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_image_label.setStyleSheet("background-color: #f0f0f0; border-radius: 8px;")  # Optional background color for visibility
        self.preview_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_image_label.setText("No Image Selected")  # Optional: Set placeholder text

        self.preview_layout.addWidget(self.preview_image_label)

        self.preview_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.preview_frame.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.preview_frame)


        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(20, 30, 20, 50)
        self.confirm_pushbutton = QPushButton(self.page_2)
        self.confirm_pushbutton.setObjectName(u"confirm_pushbutton")
        sizePolicy3.setHeightForWidth(self.confirm_pushbutton.sizePolicy().hasHeightForWidth())
        self.confirm_pushbutton.setSizePolicy(sizePolicy3)
        self.confirm_pushbutton.setMinimumSize(QSize(120, 0))
        self.confirm_pushbutton.setMaximumSize(QSize(160, 16777215))
        self.confirm_pushbutton.setFont(font2)
        self.confirm_pushbutton.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.confirm_pushbutton.setStyleSheet(u"QPushButton {\n"
"    background-color: #9c9c9c;  /* Default button color */\n"
"    color: white;\n"
"    border-radius: 10px;\n"
"    padding: 8px;\n"
"}\n"
"\n"
"QPushButton:hover{\n"
"   background-color: rgba(255, 255, 255, 0.3);  /* Soft white glow */\n"
"    color: #000000;\n"
"    border: 1px solid #cccccc;\n"
"}")
        self.confirm_pushbutton.clicked.connect(self.confirm_selection)

        self.horizontalLayout_5.addWidget(self.confirm_pushbutton)


        self.verticalLayout.addLayout(self.horizontalLayout_5)

        self.line_2 = QFrame(self.page_2)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_2)

        self.label_contact = QLabel(self.page_2)
        self.label_contact.setObjectName(u"label_contact")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.label_contact.sizePolicy().hasHeightForWidth())
        self.label_contact.setSizePolicy(sizePolicy6)
        self.label_contact.setStyleSheet(u"")
        self.label_contact.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.verticalLayout.addWidget(self.label_contact)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")

        self.verticalLayout.addLayout(self.verticalLayout_9)

        self.frame_2 = QFrame(self.page_2)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.frame_2)


        self.verticalLayout_5.addLayout(self.verticalLayout)
        self.stackedWidget.addWidget(self.page_2)
        
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")

        self.page_3_layout=QVBoxLayout(self.page_3)
        self.page_3_layout.setSpacing(0)
        self.page_3_layout.setContentsMargins(10, 10, 10, 10)

        heading_font=QFont()
        heading_font.setFamilies([u"Berlin Sans FB Demi"])
        heading_font.setPointSize(33)
        heading_font.setBold(True)
        heading_font.setItalic(False)

        # Create and configure the heading label
        self.heading_label = QLabel("RxVision")
        self.heading_label.setFont(heading_font)
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading_label.setStyleSheet("color: #6B7075;")
        self.heading_label.setFixedHeight(60) #fixed height for the header
        self.page_3_layout.addWidget(self.heading_label)

        # Create a horizontal layout for left and right panels
        self.content_layout = QHBoxLayout()

        #Create a left Panel
        self.left_scroll_area= QScrollArea()
        self.left_scroll_area.setWidgetResizable(True)
        self.left_panel=QWidget()
        self.left_layout=QVBoxLayout(self.left_panel)
        self.left_panel.setStyleSheet("background-color: #bcbcbc; border-radius: 8px;")
        self.left_layout.setSpacing(10)
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Optionally add a stretch to push items to the top
        self.left_layout.addStretch()
        self.left_panel.setLayout(self.left_layout)

        #Create a right Panel
        self.right_panel=QWidget()
        self.right_layout=QVBoxLayout(self.right_panel)
        self.right_panel.setStyleSheet("background-color: #bcbcbc; border-radius: 8px;")
        self.right_layout.setSpacing(10)
        self.right_layout.setContentsMargins(10,10,10,10)

        # Create a shadow effect
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(10)
        shadow_effect.setXOffset(0)
        shadow_effect.setYOffset(5)
        shadow_effect.setColor(QColor(0,0,0,90))  # black

        medicine_name_heading_font=QFont()
        medicine_name_heading_font.setFamilies([u"Playfair"])
        medicine_name_heading_font.setBold(True)
        medicine_name_heading_font.setPointSize(19)

        manufacturer_label=QFont()
        manufacturer_label.setFamilies([u"Arial"])
        manufacturer_label.setBold(True)
        manufacturer_label.setPointSize(10)

        composition_label=QFont()
        composition_label.setFamilies([u"Arial"])
        composition_label.setBold(True)
        composition_label.setPointSize(10)

        description_label=QFont()
        description_label.setFamilies([u"Arial"])
        description_label.setBold(True)
        description_label.setPointSize(10)

        #Name Heading Section
        self.name_label=QLabel("Name")
        self.name_label.setObjectName("name_heading")
        self.name_label.setFont(medicine_name_heading_font)
        self.name_label.setStyleSheet("background-color: #bcbcbc; padding: 10px; border-radius: 5px;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.name_label.setGraphicsEffect(shadow_effect)
        self.right_layout.addWidget(self.name_label)

        #Composition name section
        self.Composition_label=QLabel("Composition: ")
        self.Composition_label.setObjectName("composition_label")
        self.Composition_label.setFont(composition_label)
        self.Composition_label.setStyleSheet("background-color: #e0e0e0; padding: 10px; border-radius: 5px;")
        self.Composition_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.right_layout.addWidget(self.Composition_label)

        #Manufacturer name section
        self.manufacturer_label=QLabel("Manufacturer: ")
        self.manufacturer_label.setObjectName("manufacture_label")
        self.manufacturer_label.setFont(manufacturer_label)
        self.manufacturer_label.setStyleSheet("background-color: #e0e0e0; padding: 10px; border-radius: 5px;")
        self.manufacturer_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.right_layout.addWidget(self.manufacturer_label)

        # Description Section (Scrollable)
        self.description_area = QScrollArea()
        self.description_area.setWidgetResizable(True)
        self.description_widget = QLabel("Description: ")
        self.description_widget.setObjectName("description_label")
        self.description_widget.setFont(description_label)
        self.description_widget.setStyleSheet("background-color: #e0e0e0; border: 1px solid #cccccc; padding: 10px; border-radius: 5px;")
        self.description_widget.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.description_widget.setWordWrap(True)
        self.description_area.setWidget(self.description_widget)
        self.right_layout.addWidget(self.description_area)

        #Add both the panel to the main widget
        self.content_layout.addWidget(self.left_panel,35)
        self.content_layout.addWidget(self.right_panel,65)

        # Add content layout to a middle widget
        self.middle_widget = QWidget()
        self.middle_layout = QVBoxLayout(self.middle_widget)
        self.middle_layout.setContentsMargins(0, 0, 0, 0)
        self.middle_layout.addLayout(self.content_layout)

        # Add the content layout to the main page layout
        self.page_3_layout.addWidget(self.middle_widget)
        self.footer_page3=QWidget()
        self.footer_page3_layout=QVBoxLayout(self.footer_page3)
        self.footer_page3_layout.setContentsMargins(0,0,0,0)

        self.footer_label= QLabel("Contact Us @: janhavipal353@gmail.com/aujale30@gmail.com")
        footerfont=QFont()
        footerfont.setFamilies([u"Arial"])
        footerfont.setPointSize(9)

        self.footer_label.setFont(footerfont)
        self.footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer_label.setStyleSheet("color: #6B7075;")
        self.footer_page3_layout.addWidget(self.footer_label)
        self.footer_page3.setFixedHeight(50)
        self.page_3_layout.addWidget(self.footer_page3,0)

        self.stackedWidget.addWidget(self.page_3)

        self.verticalLayout_4.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"RxVision", None))
        #if QT_CONFIG(whatsthis)
        self.centralwidget.setWhatsThis(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>QStackedWidget</p></body></html>", None))
        #endif // QT_CONFIG(whatsthis)
        self.mainHeading_1.setText(QCoreApplication.translate("MainWindow", u"RxVision", None))
        self.tagline.setText(QCoreApplication.translate("MainWindow", u"\"Effortlessly extract text from any image with our advanced OCR technology\"", None))
        # self.home_image_2.setText("")
        self.pick_image_pushbutton.setText(QCoreApplication.translate("MainWindow", u"Pick an Image", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"All Rights Reserved", None))
        self.label_2.setText("")
        self.label.setText(QCoreApplication.translate("MainWindow", u"RxVision", None))
        self.home1_pushbutton.setText(QCoreApplication.translate("MainWindow", u"Home", None))
        self.extractedText_pushbutton.setText(QCoreApplication.translate("MainWindow", u"Extracted text Display", None))
        self.crop_pushbutton.setText(QCoreApplication.translate("MainWindow", u"Crop", None))
        self.confirm_pushbutton.setText(QCoreApplication.translate("MainWindow", u"Confirm Selection", None))
        self.label_contact.setText(QCoreApplication.translate("MainWindow", u"Contact Us @: janhavipal353@gmail.com / aujale30@gmail.com", None))

    def populate_medicine_labels(self,medicine_names):
        font5 = QFont()
        font5.setFamilies([u"Calibri"])
        font5.setPointSize(12)
        font5.setBold(True)
        
        #clear existing labels
        while self.left_layout.count():
            item = self.left_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        #Add medicine label or display no medicine detected
        if medicine_names:
            for index,name in enumerate (medicine_names):
                display_name= f"{index+1}. {name}"
                # name=data.get("name", f"Medicine {index + 1}")  # Default to 'Medicine X' if name is missing
                label= clickableLabel(display_name)  #Add Numbering
                label.setObjectName("medicine_name")
                label.setFont(font5)
                label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                label.setStyleSheet("QLabel{background-color: #e0e0e0; border: 1px solid #cccccc; border-radius:8px; padding:10px}"
                                    "QLabel:hover{background-color: #F4F4F9;color:#11111}"
                                    )
                
                label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                label.label_clicked = lambda name=name: self.fetch_medicine_data(name)  # Pass data to the right panel
                self.left_layout.addWidget(label)
        else:
            no_medicine_label = QLabel("No medicine detected")
            no_medicine_label.setFont(font5)
            no_medicine_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            no_medicine_label.setStyleSheet("QLabel{background-color: #e0e0e0; border: 1px solid #cccccc; border-radius:8px; padding:10px}"
                                    "QLabel:hover{background-color: #cdcece;color:#e0e0e0}"
                                    )
            no_medicine_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.left_layout.addWidget(no_medicine_label)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("RxVision")
        # Set window icon
        self.setWindowIcon(QIcon(r"resource\windowicon.ico"))
        
        #set dynamic theme of the app
        self.apply_theme()

        # Add the LoadingPage
        self.loading_page = LoadingPage(self)
        self.loading_page.setGeometry(0, 0, self.width(), self.height())
    
    def resizeEvent(self, event):
            super().resizeEvent(event)  # Ensure default behavior
            # Dynamically resize the loading page to match the window size
            self.loading_page.setGeometry(0, 0, self.width(), self.height())
            

if __name__ == "__main__":
        app= QApplication(sys.argv)
        window= MainWindow()
        window.show()
        sys.exit(app.exec())