from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from ui.navigation_bar import NavigationBar
from ui.pages.dashboard_page import DashboardPage
from ui.pages.controller_page import ControllerPage
from ui.pages.settings_page import SettingsPage
from ui.pages.logs_page import LogsPage
from ui.pages.about_page import AboutPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controller Remapper")
        self.resize(1200, 700)

        central = QWidget()
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        # Left side navbar
        self.navbar = NavigationBar(self)
        layout.addWidget(self.navbar)

        # Stack pages
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Add pages
        self.pages = {
            "dashboard": DashboardPage(),
            "controllers": ControllerPage(),
            "settings": SettingsPage(),
            "logs": LogsPage(),
            "about": AboutPage()
        }

        for p in self.pages.values():
            self.stack.addWidget(p)

        self.navbar.page_selected.connect(self.show_page)

        self.setCentralWidget(central)
        self.show_page("dashboard")

    def show_page(self, page_name: str):
        widget = self.pages.get(page_name)
        if widget:
            self.stack.setCurrentWidget(widget)
