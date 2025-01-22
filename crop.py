from PyQt6.QtWidgets import QLabel, QDialog, QPushButton, QVBoxLayout, QSizePolicy, QScrollArea
from PyQt6.QtGui import QPixmap, QPainter, QPen, QImage, QIcon, QFont, QFontDatabase, QTransform
from PyQt6.QtCore import Qt, QRect
from text_extraction import extract_text_from_image
class CropImageDialog(QDialog):

    def update_image_display(self):
        self.image_label.setPixmap(self.pixmap)
        self.layout.addWidget(self.image_label)

    def rotate_image(self):
        transform = QTransform().rotate(90)  # Rotate by 90 degrees
        self.pixmap = self.pixmap.transformed(transform)
        self.update_image_display()

    def __init__(self, image_path,medicine_dataset, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crop Image")
        self.setWindowIcon(QIcon(r"resource\cropwindow.png"))
        self.image_path = image_path
        self.rotation_angle=0 #To keep track of the orientation of the image
        self.scale_factor= 1.0 #initial scale factor of the image

        # Set a maximum size for the dialog
        max_width = 800  # Set your maximum width
        max_height = 800  # Set your maximum height
        self.setMaximumSize(max_width, max_height)


        # Initialize pixmap with the image
        self.pixmap = QPixmap(image_path)  # Ensure image_path is a valid path

        # Scale the image if it's larger than the maximum size
        scaled_pixmap = self.pixmap
        if self.pixmap.width() > max_width or self.pixmap.height() > max_height:
            scaled_pixmap = self.pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio)

        # Set a maximum size for the dialog
        # max_width = 800  # Set your maximum width
        # max_height = 600  # Set your maximum height
        # scaled_pixmap = self.pixmap.scaled(max_width, max_height, Qt.AspectRatioMode.KeepAspectRatio)

        
        
        self.pixmap = scaled_pixmap

        # Scroll Area to hold the image label (allows scrolling for large images)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.image_label = QLabel(self)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        # QLabel to show the image (for cropping)
        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.pixmap)

        # Add rotate button
        self.rotate_button = QPushButton("Rotate", self)
        self.rotate_button.clicked.connect(self.rotate_image)
        self.rotate_button.setFixedSize(100, 40)

        
        # Add a confirm button
        self.confirm_button = QPushButton("Confirm", self)
        self.confirm_button.clicked.connect(self.confirm_crop)
        self.confirm_button.setFixedSize(100, 40)
        self.confirm_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        # self.confirm_button.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font= QFont()
        font.setFamilies([u"Calibri"])
        font.setPointSize(12)
        font.setBold(True)
        self.confirm_button.setFont(font)
        self.confirm_button.setStyleSheet(
            """
            QPushButton {
                color: #ffffff;
                background-color: #9c9c9c;
                border-radius: 9px;
                font.setFamilies([u"Berlin Sans FB Demi"])
            }
            QPushButton:hover {
                color: #111111;
                background-color: #ffffff;
                border: 1px solid #cccccc;
            }
            QPushButton:pressed {
                background-color: #38454C;  /* Darker background when pressed */
                padding-top: 5px;  /* Slightly decrease padding for pressed effect */
                padding-left: 10px;  /* Slightly decrease padding for pressed effect */
            }
            """
        )

        # Set layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.confirm_button)
        self.layout.addWidget(self.confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)  # Center the button in the layout

        # Variables for cropping
        self.crop_start = None
        self.crop_end = None
        self.crop_rect = QRect()
        self.is_cropping = False

        # Add mouse wheel event
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
    def update_scaled_pixmap(self):
        # Scale the image based on the scale factor
        self.scaled_pixmap = self.pixmap.scaled(self.pixmap.size() * self.scale_factor, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_label.setPixmap(self.scaled_pixmap)

        # Update the size of the image label to the scaled pixmap size
        self.image_label.setFixedSize(self.scaled_pixmap.size())

    def wheelEvent(self, event):
        # Zoom in or out based on the scroll direction
        zoom_in = event.angleDelta().y() > 0
        if zoom_in:
            self.scale_factor *= 1.1  # Zoom in
        else:
            self.scale_factor /= 1.1  # Zoom out
        self.update_scaled_pixmap()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_cropping = True
            self.crop_start = event.pos()

    def mouseMoveEvent(self, event):
        if self.is_cropping:
            self.crop_end = event.pos()
            self.update_crop()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_cropping = False
            self.crop_end = event.pos()
            self.update_crop()

    def update_crop(self):
        # Update the cropping rectangle
        self.crop_rect = QRect(self.crop_start, self.crop_end)
        # Redraw the label to show the updated rectangle
        self.image_label.setPixmap(self.get_cropped_image_with_overlay())

    def get_cropped_image_with_overlay(self):
        # Create a new QImage with the original image
        overlay_image = self.pixmap.toImage()
        
        # Draw the cropping rectangle
        painter = QPainter(overlay_image)
        pen = QPen(Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        painter.drawRect(self.crop_rect)
        painter.end()
        
        return QPixmap.fromImage(overlay_image)

    def confirm_crop(self):
        if not self.crop_rect.isNull():
            # Get the cropping coordinates
            x1, y1 = self.crop_rect.topLeft().x(), self.crop_rect.topLeft().y()
            x2, y2 = self.crop_rect.bottomRight().x(), self.crop_rect.bottomRight().y()

            # Crop the image
            cropped_pixmap = self.pixmap.copy(x1, y1, x2 - x1, y2 - y1)

            # Set the cropped pixmap in the QLabel
            self.image_label.setPixmap(cropped_pixmap)

            # Save the cropped image to a file (you can choose a better path or naming strategy)
            cropped_image_path = "cropped_image.png"
            cropped_pixmap.save(cropped_image_path)  # Save the cropped image

             # Load the cropped image back as QPixmap to set in the preview label
            cropped_pixmap = QPixmap(cropped_image_path)

             # Call the text extraction function and pass the cropped image
            extracted_text = extract_text_from_image(r"cropped_image.png")  # Pass the saved cropped image path

             # Save or return the cropped image
            cropped_pixmap.save("cropped_image.png")  # Save the cropped image

            # Close the dialog and confirm the crop
            self.accept()
            
            return cropped_image_path
        return None

def open_crop_window(image_path):
    dialog = CropImageDialog(image_path)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        # Cropping confirmed, return the cropped image
        return dialog.confirm_crop()  # Return the cropped image pat
    return None