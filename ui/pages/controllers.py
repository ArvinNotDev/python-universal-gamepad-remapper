from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class ControllersPage(QWidget):
    def __init__(self):
        super().__init__()
        layout_controllers = QVBoxLayout(self)

        lbl_controllers = QLabel("Controllers Page")
        lbl_controllers.setAlignment(Qt.AlignCenter)

        layout_controllers.addWidget(lbl_controllers)
