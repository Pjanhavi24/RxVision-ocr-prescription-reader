import requests
import logging
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QIcon

# Set up logging
logging.basicConfig(
    filename="error_log.txt",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def check_internet_connection(parent=None):
    """Check if the internet is connected."""
    try:
        # Try to reach a reliable website (e.g., Google)
        response = requests.get("https://www.google.com", timeout=5)
        if response.status_code == 200:
            if parent:
                QMessageBox.information(
                    parent,
                    "Internet Connection",
                    "<h2 style='color:green;'>Internet is Connected</h2>"
                    "<p>Your internet connection is active. You can proceed with online features.</p>",
                    QMessageBox.StandardButton.Ok
                )
            return True
    except requests.ConnectionError:
        if parent:
            msg_box = QMessageBox(parent)
            msg_box.setWindowTitle("No Internet Connection ⚠️ ")
            msg_box.setText("<h2 style='color:red;'>No Internet</h2>")
            msg_box.setInformativeText(
                "<p style='font-size:14px;'>It seems like your internet connection is not active. "
                "Please check your network settings and try again.</p>"
            )
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
        return False
    except Exception as e:
        logging.error(f"Unexpected error during internet check: {e}")
        if parent:
            msg_box = QMessageBox(parent)
            msg_box.setWindowTitle("Unexpected Error ❌")
            msg_box.setText("<h2 style='color:orange;'>Unexpected Error</h2>")
            msg_box.setInformativeText(
                "<p style='font-size:14px;'>An error occurred while checking the internet connection. "
                "Please try again later or contact support if the issue persists.</p>"
            )
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()
        return False
