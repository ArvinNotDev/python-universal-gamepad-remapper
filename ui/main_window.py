import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QStackedWidget,
    QSystemTrayIcon, QMenu, QApplication
)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QIcon, QAction

from ui.theme_manager import ThemeManager
from ui.pages.dashboard import DashboardPage
from ui.pages.controllers import ControllersPage
from ui.pages.settings import SettingsPage

from core.settings import SettingsManager


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.theme_manager = ThemeManager(app)
        self.theme_manager.apply_theme("dark")
        self.settings = SettingsManager()

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
        self.pages.addWidget(DashboardPage(self.settings))
        self.pages.addWidget(ControllersPage())
        self.pages.addWidget(SettingsPage(self.theme_manager, self.settings))

        # Add menu + pages to root layout
        main_layout.addWidget(self.menu)
        main_layout.addWidget(self.pages, 1)

        # Page switching
        self.menu.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.menu.setCurrentRow(0)

        # ---------- SYSTEM TRAY ICON ----------
        # Only create tray if platform supports it
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            icon = QIcon("ui/assets/tray.png")
            # fallback to theme icon if file not found
            if icon.isNull():
                icon = QIcon.fromTheme("applications-system")
            self.tray_icon.setIcon(icon)
            self.tray_icon.setToolTip("Universal Remapper")
            self._create_tray_menu()
            self.tray_icon.activated.connect(self._on_tray_activated)
            self.tray_icon.show()
            self._shown_tray_hint = False
        else:
            self.tray_icon = None

    def _create_tray_menu(self):
        """Create and attach tray context menu."""
        menu = QMenu(self)

        show_action = QAction("Show", menu)
        show_action.triggered.connect(self._show_from_tray)

        hide_action = QAction("Hide", menu)
        hide_action.triggered.connect(self.hide)

        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(QApplication.instance().quit)

        menu.addActions([show_action, hide_action, quit_action])
        self.tray_icon.setContextMenu(menu)

    def _on_tray_activated(self, reason):
        """
        Handle clicks on the system tray icon.
        Toggle show/hide on single/double click depending on platform.
        """
        # ActivationReason is an enum defined on QSystemTrayIcon
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.isVisible() and not self.isMinimized():
                self.hide()
            else:
                self._show_from_tray()

    def _show_from_tray(self):
        """Restore and raise the window when requested from tray."""
        self.show()
        # If minimized, restore normal state first
        if self.isMinimized():
            self.setWindowState(self.windowState() & ~Qt.WindowMinimized)
        self.activateWindow()
        self.raise_()

    def closeEvent(self, event):
        """
        Instead of closing the application when the window is closed,
        hide it to the tray (if available) and ignore the close event.
        This is common behavior for tray-based utilities.
        """
        if self.tray_icon is not None:
            # hide to tray
            self.hide()
            # Optionally show a one-time balloon telling user app is still running
            if not getattr(self, "_shown_tray_hint", False):
                try:
                    self.tray_icon.showMessage(
                        "Universal Remapper",
                        "Application is still running in the tray. Use the tray icon to restore or quit.",
                    )
                except Exception:
                    # showMessage can fail on platforms without notifications support
                    pass
                self._shown_tray_hint = True
            event.ignore()  # prevent the window from being destroyed
        else:
            # No tray available — perform normal close
            super().closeEvent(event)
