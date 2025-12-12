import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.hid import HIDManager

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Universal Remapper")
    hid_manager = HIDManager(poll_interval=0)
    window = MainWindow(hid_manager, app)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
