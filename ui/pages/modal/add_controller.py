from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QListWidget, QHBoxLayout, QDialogButtonBox
from PySide6.QtCore import Qt

class AddControllerDialog(QDialog):
    """
    A modal dialog that presents two lists:
    - HID device list
    - Emulated controller list
    Returns selected items via exec_().
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Controller")
        self.setModal(True)
        self.resize(400, 300)

        main_layout = QVBoxLayout(self)

        # Title
        lbl_title = QLabel("Select HID Device and Emulated Controller")
        lbl_title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(lbl_title)

        # Content layout
        lists_layout = QHBoxLayout()

        # HID List
        self.hid_list = QListWidget()
        self.hid_list.setSelectionMode(QListWidget.SingleSelection)
        lists_layout.addWidget(self.hid_list)

        # Emulated Controller List
        self.emu_list = QListWidget()
        self.emu_list.setSelectionMode(QListWidget.SingleSelection)
        lists_layout.addWidget(self.emu_list)

        main_layout.addLayout(lists_layout)

        # Buttons (Apply / Cancel)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            orientation=Qt.Horizontal
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
             
    def get_selections(self):
        """
        Returns (hid_device, emu_device) or (None, None) if nothing selected.
        """
        hid = None
        emu = None

        if self.hid_list.currentItem() is not None:
            hid = self.hid_list.currentItem().text()

        if self.emu_list.currentItem() is not None:
            emu = self.emu_list.currentItem().text()

        return hid, emu
