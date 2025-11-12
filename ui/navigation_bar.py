from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt

class NavigationBar(QWidget):
    page_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)

        buttons = {
            "Dashboard": "dashboard",
            "Controllers": "controllers",
            "Settings": "settings",
            "Logs": "logs",
            "About": "about"
        }

        for text, page in buttons.items():
            btn = QPushButton(text)
            btn.clicked.connect(lambda _, p=page: self.page_selected.emit(p))
            layout.addWidget(btn)

        layout.addStretch()
