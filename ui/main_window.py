import sys
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QSystemTrayIcon,
    QMenu,
    QApplication,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction

from ui.theme_manager import ThemeManager
from ui.pages.controller_emulation import ControllerEmulation
from ui.pages.controllers import ControllersPage
from ui.pages.settings import SettingsPage
from ui.pages.server import ServerPage
from ui.pages.hotkey import HotkeyPage
from core.settings import SettingsManager

from core.utils.hotkeys import Hotkey

class MainWindow(QMainWindow):

    WINDOW_TITLE = "Universal Remapper"
    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 700

    # Menu indices (must match the order items are added to self.menu)
    IDX_CONTROLLER_EMULATION = 0
    IDX_REMOTE_GAMEPAD = 1
    IDX_HOTKEY = 2
    IDX_TEST_XINPUT = 3
    IDX_SETTINGS = 4
    IDX_QUIT = 5

    def __init__(self, app: QApplication) -> None:
        super().__init__()

        # Theme & settings
        self.theme_manager = ThemeManager(app)
        self.theme_manager.apply_theme("dark")
        self.media_functions = {
                "volume up": "volume up",
                "volume down": "volume down",
                "play/pause media": "play/pause media",
                "next track": "next track",
                "previous track": "previous track",
                "volume mute": "volume mute",
            }
        self.hotkey = Hotkey("hotkeys.json")
        self.settings = SettingsManager()

        # quitting flag
        self._is_quitting = False

        self.setWindowTitle(self.WINDOW_TITLE)
        self.resize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        self._shown_tray_hint = False

        # Central layout
        central = QWidget(self)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central)

        # Left column
        left_column = QVBoxLayout()
        left_column.setContentsMargins(10, 10, 10, 10)

        self.menu = QListWidget()
        self.menu.setFixedWidth(200)

        # Disable scrolling completely
        self.menu.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.menu.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.menu.setSelectionMode(QListWidget.SingleSelection)

        # Menu items (order must match the constants above)
        self.menu.addItem(QListWidgetItem("Controller Emulation"))  # 0
        self.menu.addItem(QListWidgetItem("Remote Gamepad"))        # 1
        self.menu.addItem(QListWidgetItem("Hotkeys"))               # 2
        self.menu.addItem(QListWidgetItem("Test XInput"))           # 3
        self.menu.addItem(QListWidgetItem("Settings"))              # 4
        self.menu.addItem(QListWidgetItem("Quit"))                  # 5

        # Force menu to fit all items
        item_height = self.menu.sizeHintForRow(0)
        total_height = item_height * self.menu.count() + 2 * self.menu.frameWidth()
        self.menu.setFixedHeight(total_height)

        left_column.addWidget(self.menu)
        left_column.addStretch()

        # Pages
        self.pages = QStackedWidget()

        controllers_page = ControllersPage()
        hotkey_page = HotkeyPage(self.hotkey)
        # The order here must match indices 0..4
        # 0: Controller Emulation
        self.pages.addWidget(ControllerEmulation(self.settings, controllers_page, hotkey_page))
        # 1: Remote Gamepad (server page)
        self.pages.addWidget(ServerPage(self.settings, controllers_page))
        # 2: Hotkeys page
        self.pages.addWidget(hotkey_page)
        # 3: Test XInput
        self.pages.addWidget(controllers_page)
        # 4: Settings
        self.pages.addWidget(SettingsPage(self.theme_manager, self.settings))

        main_layout.addLayout(left_column)
        main_layout.addWidget(self.pages, 1)

        self.menu.currentRowChanged.connect(self._on_menu_index_changed)
        self.menu.setCurrentRow(self.IDX_CONTROLLER_EMULATION)

        # Tray
        self.tray_icon: QSystemTrayIcon | None = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            self._init_tray_icon()

    # --------------------
    # Menu
    # --------------------

    def _on_menu_index_changed(self, index: int) -> None:
        # If Quit item selected
        if index == self.IDX_QUIT:
            self._is_quitting = True
            QApplication.quit()
            return

        # For all other indices, show corresponding page (indices 0..4)
        if 0 <= index < self.pages.count():
            self.pages.setCurrentIndex(index)

    # --------------------
    # Tray
    # --------------------

    def _init_tray_icon(self) -> None:

        tray_icon = QSystemTrayIcon(self)

        icon = QIcon("ui/assets/tray.png")
        if icon.isNull():
            icon = QIcon.fromTheme("applications-system")

        tray_icon.setIcon(icon)
        tray_icon.setToolTip(self.WINDOW_TITLE)

        self.tray_icon = tray_icon
        self._create_tray_menu()

        tray_icon.activated.connect(self._on_tray_activated)
        tray_icon.show()

    def _create_tray_menu(self) -> None:

        if self.tray_icon is None:
            return

        menu = QMenu(self)

        show_action = QAction("Show", menu)
        show_action.triggered.connect(self._show_from_tray)

        hide_action = QAction("Hide", menu)
        hide_action.triggered.connect(self.hide)

        quit_action = QAction("Quit", menu)

        def _tray_quit():
            self._is_quitting = True
            QApplication.quit()

        quit_action.triggered.connect(_tray_quit)

        menu.addActions([show_action, hide_action, quit_action])
        self.tray_icon.setContextMenu(menu)

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:

        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):

            if self.isVisible() and not self.isMinimized():
                self.hide()
            else:
                self._show_from_tray()

    def _show_from_tray(self) -> None:

        self.show()

        if self.isMinimized():
            self.setWindowState(self.windowState() & ~Qt.WindowMinimized)

        self.activateWindow()
        self.raise_()

    # --------------------
    # Close behavior
    # --------------------

    def closeEvent(self, event) -> None:
        # If we are quitting explicitly (from menu or tray), exit
        if self._is_quitting:
            event.accept()
            return

        # Otherwise, go to tray (if available)
        if self.tray_icon is not None:

            self.hide()

            if not self._shown_tray_hint:
                try:
                    self.tray_icon.showMessage(
                        self.WINDOW_TITLE,
                        "Application is still running in the tray. "
                        "Use the tray icon to restore or quit.",
                    )
                except Exception:
                    pass

                self._shown_tray_hint = True

            event.ignore()
        else:
            super().closeEvent(event)

