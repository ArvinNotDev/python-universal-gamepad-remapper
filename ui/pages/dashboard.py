from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QDialog, QListWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize

from ui.pages.modal.add_controller import AddControllerDialog

from core.hid import HIDManager

class EmuListItemWidget(QWidget):
    """
    Widget used inside QListWidget for each emulated device entry.

    Shows:
    [ text (HID → EMU) ] [ Emulate button ] [ status indicator ]

    Emits:
    emulate_requested(hid, emu, widget) when the 'Emulate' button is clicked.
    """
    emulate_requested = Signal(str, str, object)
    delete_requested = Signal(object)

    def __init__(self, hid: str, emu: str, parent=None):
        super().__init__(parent)
        self.hid = hid
        self.emu = emu
        self._running = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self.lbl_text = QLabel(f"{hid} → {emu}")
        self.lbl_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.lbl_text)

        self.btn_emulate = QPushButton("Emulate")
        self.btn_emulate.setToolTip("Start/stop emulation for this mapping")
        self.btn_emulate.clicked.connect(self._on_emulate_clicked)
        layout.addWidget(self.btn_emulate)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setToolTip("Remove this mapping")
        self.btn_delete.clicked.connect(self._on_delete_clicked)
        layout.addWidget(self.btn_delete)

        self.status = QLabel()
        self.status.setFixedSize(12, 12)
        self.status.setToolTip("Running status")
        self._update_status_style(False)
        layout.addWidget(self.status, alignment=Qt.AlignRight)
        
        
    def _update_status_style(self, running: bool):
        """Update status indicator appearance."""
        if running:
            color = "#2ecc71"
        else:
            color = "#9aa0a6"
        self.status.setStyleSheet(
            f"border-radius: 6px; background-color: {color};"
        )

    def set_running(self, running: bool):
        """Public method to set running indicator state."""
        self._running = bool(running)
        self._update_status_style(self._running)
        self.btn_emulate.setText("Stop" if self._running else "Emulate")

    def is_running(self) -> bool:
        return self._running

    def _on_emulate_clicked(self):
        """
        Emit emulate_requested; the DashboardPage should connect to this
        and implement actual logic. We also toggle the visual state here
        as a placeholder so the UI responds immediately.
        """
        self.set_running(not self._running)
        self.emulate_requested.emit(self.hid, self.emu, self)
    def _on_delete_clicked(self):
        self.delete_requested.emit(self)

class DashboardPage(QWidget):
    """
    Dashboard page that contains a QListWidget of emulated mappings.
    Each mapping row contains an Emulate button and a running indicator.
    """
    def __init__(self, hid_manager):
        super().__init__()

        layout_dashboard = QVBoxLayout(self)

        self.devices = hid_manager.scan_devices()

        lbl_dashboard = QLabel("Dashboard Page")
        lbl_dashboard.setAlignment(Qt.AlignCenter)

        emu_label = QLabel("List of Emulated Devices")
        emu_label.setAlignment(Qt.AlignCenter)

        self.emu_list = QListWidget()

        add_btn = QPushButton("Add Controller")
        add_btn.clicked.connect(self.open_add_controller_dialog)

        layout_dashboard.addWidget(lbl_dashboard)
        layout_dashboard.addWidget(emu_label)
        layout_dashboard.addWidget(self.emu_list)
        layout_dashboard.addWidget(add_btn)

    def open_add_controller_dialog(self):
        dialog = AddControllerDialog(self)

        hid_list = []
        product_counter = 0
        previous_device = None
        for h in self.devices:
            hid_name = h["product_string"]
            if previous_device == hid_name:
                hid_name = str(product_counter) + hid_name
            else:
                product_counter = 0
            hid_list.append(h["product_string"])
            previous_device = h["product_string"]

        dialog.hid_list.addItems(hid_list)
        dialog.emu_list.addItems(["Emulate Xbox"])

        if dialog.exec_() == QDialog.Accepted:
            hid_choice, emu_choice = dialog.get_selections()
            if hid_choice and emu_choice:
                self.add_emulated_mapping(hid_choice, emu_choice)

    def add_emulated_mapping(self, hid: str, emu: str):
        """
        Adds an item widget to the emu_list showing the mapping,
        an emulate button and a status indicator.
        """
        item = QListWidgetItem()
        widget = EmuListItemWidget(hid, emu)

        item.setSizeHint(widget.sizeHint())

        item.setData(Qt.UserRole, (hid, emu))

        self.emu_list.addItem(item)
        self.emu_list.setItemWidget(item, widget)

        widget.emulate_requested.connect(self._on_emulate_requested)
        widget.delete_requested.connect(lambda w=widget, i=item: self._on_delete_requested(w, i))

    def _on_emulate_requested(self, hid: str, emu: str, widget: EmuListItemWidget):
        """
        Called when a row's Emulate button is clicked.
        """
        running = widget.is_running()
        print(f"[DashboardPage] Emulate requested: HID={hid}, EMU={emu}, running={running}")

        if running:
            self.start_emulation()
        else:
            self.stop_emulation()
    def _on_delete_requested(self, widget: EmuListItemWidget, item: QListWidgetItem):
        self.emu_list.takeItem(self.emu_list.row(item))

    def start_emulation(self):
        pass

    def stop_emulation(self):
        pass
