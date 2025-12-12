from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QStackedWidget
)
from PySide6.QtCore import Qt

from ui.theme_manager import ThemeManager
from ui.pages.dashboard import DashboardPage
from ui.pages.controllers import ControllersPage
from ui.pages.settings import SettingsPage

class MainWindow(QMainWindow):
    def __init__(self, hid_manager, app):
        super().__init__()
        self.theme_manager = ThemeManager(app)
        self.theme_manager.apply_theme("dark")

        self.setWindowTitle("Universal Remapper")
        self.resize(900, 500)

        # ---------- CENTRAL ROOT ----------
        central = QWidget(self)
        main_layout = QHBoxLayout(central)
        self.setCentralWidget(central)

        # ---------- LEFT MENU ----------
        self.menu = QListWidget()
        self.menu.setFixedWidth(200)
        self.menu.setSpacing(10)


        self.menu.addItem(QListWidgetItem("Dashboard"))
        self.menu.addItem(QListWidgetItem("Controllers"))
        self.menu.addItem(QListWidgetItem("Settings"))

        # ---------- STACKED PAGES ----------
        self.pages = QStackedWidget()

        # Add pages to stacked widget
        self.pages.addWidget(DashboardPage(hid_manager))
        self.pages.addWidget(ControllersPage())
        self.pages.addWidget(SettingsPage(self.theme_manager))

        # Add menu + pages to root layout
        main_layout.addWidget(self.menu)
        main_layout.addWidget(self.pages, 1)

        # Page switching
        self.menu.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.menu.setCurrentRow(0)
