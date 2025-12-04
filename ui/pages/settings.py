from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout_settingsPage = QVBoxLayout(self)

        lbl_settings = QLabel("Settings Page")
        lbl_settings.setAlignment(Qt.AlignCenter)

        layout_settingsPage.addWidget(lbl_settings)
