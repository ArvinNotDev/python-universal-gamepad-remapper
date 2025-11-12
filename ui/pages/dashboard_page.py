from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.components.status_card import StatusCard

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Dashboard Overview"))
        layout.addWidget(StatusCard("Connected Controllers", "2"))
        layout.addWidget(StatusCard("Virtual Devices", "1"))
