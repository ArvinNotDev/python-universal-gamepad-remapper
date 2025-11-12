from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Settings Page"))
