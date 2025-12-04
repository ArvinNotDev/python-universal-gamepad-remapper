from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PySide6.QtCore import Qt

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()

        layout_dashboard = QVBoxLayout(self)

        lbl_dashboard = QLabel("Dashboard Page")
        lbl_dashboard.setAlignment(Qt.AlignCenter)

        emu_label = QLabel("list of emulated devices")
        emu_label.setAlignment(Qt.AlignCenter)

        emu_list = QListWidget()

        layout_dashboard.addWidget(lbl_dashboard)
        layout_dashboard.addWidget(emu_label)
        layout_dashboard.addWidget(emu_list)