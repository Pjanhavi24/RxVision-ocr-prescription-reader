from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QSizePolicy
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QSize, Qt
import sys
import os
import cv2

def open_file_dialog(self):
    # Open the file dialog to pick an image file
    file_dialog = QFileDialog(self)
    file_path, _ = file_dialog.getOpenFileName(self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")

    if file_path:
        # # Load and display the selected image in the label
        self.selected_image_path= file_path   # <-- this line saves the path
        self.stackedWidget.setCurrentIndex(1)  # Switch to page 2

        img = cv2.imread(file_path)

        #Get the dimensions of the Qlabel
        label_width= self.preview_image_label.width()
        label_height= self.preview_image_label.height()

        #Get the original image size
        img_height, img_width, _ = img.shape

        # Get the aspect ratio of the image and the label
        aspect_ratio_img= img_width/img_height
        aspect_ratio_label= label_width/label_height

         # Resize while maintaining aspect ratio, and fill the empty space
        if aspect_ratio_img > aspect_ratio_label:
            # Image is wider than QLabel: Fit to width, leave space on top and bottom
            new_width = label_width
            new_height = int(label_width / aspect_ratio_img)
        else:
            # Image is taller than QLabel: Fit to height, leave space on sides
            new_height = label_height
            new_width = int(label_height * aspect_ratio_img)

         # Resize the image using OpenCV
        resized_img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA if (new_width < img_width or new_height < img_height) else cv2.INTER_CUBIC)

        # resize the image using the opencv's INTERCUBIC for upscaling and INTER_AREA for downscaling the image
        # if img_width > label_width or img_height > label_height:
        #     # Downscale using INTER_AREA to prevent blurring
        #     resized_img = cv2.resize(img, (label_width, label_height), interpolation=cv2.INTER_AREA)
        # else:
        #     # Upscale using INTER_CUBIC, which provides better quality for enlarging
        #     # resized_img = cv2.resize(img, (label_width, label_height), interpolation=cv2.INTER_CUBIC)
        #     resized_img= img
        
        # Convert the resized image back to a QPixmap
        resized_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)  # Convert to RGB

        height, width, channel = resized_img.shape
        bytes_per_line = 3 * width
        q_img = QPixmap(QImage(resized_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888))


        # Ensure the QLabel has the correct size before scaling the image
        # self.preview_image_label.setMinimumSize(1, 1)  # Forces minimum size

        # self.preview_image_label.setPixmap(pixmap.scaled(
        #     self.preview_image_label.width(),
        #     self.preview_image_label.height(),
        #     Qt.AspectRatioMode.KeepAspectRatio,
        #     Qt.TransformationMode.SmoothTransformation
        #     ))

        #Resize the Qlabel to fit the frame
        self.preview_image_label.setPixmap(q_img) #Resize the label to fit the preview frame
        self.preview_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter) #Center the image


        # Ensure the QLabel expands to fill the available space
        self.preview_image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Force a layout update
        self.preview_image_label.update()

        # Resize the QLabel to fit the frame
        self.preview_image_label.resize(self.preview_frame.size())
        self.preview_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the image

        # Use file_path for further processing as needed
        pass
