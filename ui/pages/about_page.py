from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("<b>Controller Remapper</b><br>Version 1.0"))
        layout.addWidget(QLabel("Created by Arveen"))
