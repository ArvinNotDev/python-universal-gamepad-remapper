from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QStackedWidget
)
from PySide6.QtCore import Qt

from ui.pages.dashboard import DashboardPage
from ui.pages.controllers import ControllersPage
from ui.pages.settings import SettingsPage

class MainWindow(QMainWindow):
    def __init__(self, hid_manager):
        super().__init__()

        self.setWindowTitle("Universal Remapper")
        self.resize(900, 500)

        # ---------- CENTRAL ROOT ----------
        central = QWidget(self)
        main_layout = QHBoxLayout(central)
        self.setCentralWidget(central)

        # ---------- LEFT MENU ----------
        self.menu = QListWidget()
        self.menu.setFixedWidth(180)
        self.menu.setSpacing(4)
        self.menu.setStyleSheet("""
            QListWidget {
                background-color: #2d2d30;
                border: none;
                color: white;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #3e3e42;
            }
        """)

        self.menu.addItem(QListWidgetItem("Dashboard"))
        self.menu.addItem(QListWidgetItem("Controllers"))
        self.menu.addItem(QListWidgetItem("Settings"))

        # ---------- STACKED PAGES ----------
        self.pages = QStackedWidget()

        # Add pages to stacked widget
        self.pages.addWidget(DashboardPage(hid_manager))
        self.pages.addWidget(ControllersPage())
        self.pages.addWidget(SettingsPage())

        # Add menu + pages to root layout
        main_layout.addWidget(self.menu)
        main_layout.addWidget(self.pages, 1)

        # Page switching
        self.menu.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.menu.setCurrentRow(0)
