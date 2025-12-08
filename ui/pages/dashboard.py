from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QDialog, QListWidgetItem, QSizePolicy, QMessageBox
)
from PySide6.QtCore import Qt, Signal

from ui.pages.modal.add_controller import AddControllerDialog

from core.mapper import Mapper


class EmuListItemWidget(QWidget):
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
        if running:
            color = "#2ecc71"
        else:
            color = "#9aa0a6"
        self.status.setStyleSheet(
            f"border-radius: 6px; background-color: {color};"
        )

    def set_running(self, running: bool):
        self._running = bool(running)
        self._update_status_style(self._running)
        self.btn_emulate.setText("Stop" if self._running else "Emulate")

    def is_running(self) -> bool:
        return self._running

    def _on_emulate_clicked(self):
        self.set_running(not self._running)
        self.emulate_requested.emit(self.hid, self.emu, self)

    def _on_delete_clicked(self):
        self.delete_requested.emit(self)


class DashboardPage(QWidget):
    def __init__(self, hid_manager):
        super().__init__()
        layout_dashboard = QVBoxLayout(self)

        self.hid_manager = hid_manager
        self.mappers = {}

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

        hid_list_display = []
        hid_path_list = []

        devices = self.hid_manager.scan_devices() or []

        name_counts = {}
        for dev in devices:
            name = dev.get("product_string") or f"VID_{dev.get('vendor_id')}_PID_{dev.get('product_id')}"
            count = name_counts.get(name, 0)
            name_counts[name] = count + 1
            display = name if count == 0 else f"{name} ({count})"
            hid_list_display.append(display)
            hid_path_list.append(dev)

        dialog.hid_list.addItems(hid_list_display)
        dialog.emu_list.addItems(["Emulate Xbox"])

        if dialog.exec_() == QDialog.Accepted:
            hid_choice, emu_choice = dialog.get_selections()
            if hid_choice and emu_choice:
                added = self.add_emulated_mapping(hid_choice, emu_choice)
                if not added:
                    return

                selected_index = -1
                try:
                    selected_index = dialog.hid_list.currentRow()
                except Exception:
                    selected_index = -1

                if selected_index is None or selected_index < 0:
                    try:
                        selected_index = hid_list_display.index(hid_choice)
                    except ValueError:
                        selected_index = -1

                if 0 <= selected_index < len(hid_path_list):
                    device = hid_path_list[selected_index]
                    self.hid_manager.start_polling(device["vendor_id"], device["product_id"], device["path"])
                else:
                    print("[DashboardPage] Warning: selected HID could not be mapped to a device entry.")

    def add_emulated_mapping(self, hid: str, emu: str) -> bool:
        for i in range(self.emu_list.count()):
            existing_item = self.emu_list.item(i)
            existing_data = existing_item.data(Qt.UserRole)
            if existing_data and existing_data[0] == hid:
                self.emu_list.setCurrentItem(existing_item)
                existing_widget = self.emu_list.itemWidget(existing_item)
                if existing_widget:
                    existing_widget.setFocus()
                QMessageBox.information(self, "Already added",
                                        f"HID '{hid}' is already in the emulated devices list.")
                return False

        item = QListWidgetItem()
        widget = EmuListItemWidget(hid, emu)

        item.setSizeHint(widget.sizeHint())
        item.setData(Qt.UserRole, (hid, emu))

        self.emu_list.addItem(item)
        self.emu_list.setItemWidget(item, widget)

        widget.emulate_requested.connect(self._on_emulate_requested)
        widget.delete_requested.connect(lambda w=widget, i=item: self._on_delete_requested(w, i))

        return True

    def _find_device_by_display_name(self, display_name: str):
        devices = getattr(self.hid_manager, "devices", None) or self.hid_manager.scan_devices() or []
        base_name = display_name.split(" (")[0]
        for dev in devices:
            name = dev.get("product_string") or f"VID_{dev.get('vendor_id')}_PID_{dev.get('product_id')}"
            if base_name == name:
                return dev
        return None

    def _on_emulate_requested(self, hid: str, emu: str, widget: EmuListItemWidget):
        running = widget.is_running()
        device = self._find_device_by_display_name(hid)
        if not device:
            print("[DashboardPage] Could not match HID to device")
            widget.set_running(False)
            return

        path = device.get("path")
        if running:
            if path in self.mappers:
                return

            controller = self.hid_manager.start_polling(
                device.get("vendor_id"),
                device.get("product_id"),
                device.get("path")
            )

            vid = device.get("vendor_id")
            pid = device.get("product_id")
            try:
                vid_int = int(vid) if isinstance(vid, (int,)) else int(str(vid), 0)
            except Exception:
                try:
                    vid_int = int(vid)
                except Exception:
                    vid_int = None
            try:
                pid_int = int(pid) if isinstance(pid, (int,)) else int(str(pid), 0)
            except Exception:
                try:
                    pid_int = int(pid)
                except Exception:
                    pid_int = None

            if vid_int == 0x054C and pid_int in (0x05C4, 0x09CC):
                controller_type = "Dualshock4"
            elif vid_int == 0x054C and pid_int == 0x0CE6:
                controller_type = "Dualsense"
            else:
                controller_type = "Generic"

            mapper = Mapper(controller, controller_type, "x360")
            self.mappers[path] = mapper

            worker = None
            wtuple = self.hid_manager._workers.get(path)
            if wtuple:
                _, worker, _ = wtuple
            if worker:
                worker.data_received.connect(mapper.handle_hid_data)
                worker.error.connect(mapper.handle_error)

            mapper.start()

        else:
            if path in self.mappers:
                mapper = self.mappers[path]
                mapper.stop()
                try:
                    wtuple = self.hid_manager._workers.get(path)
                    if wtuple:
                        _, worker, _ = wtuple
                        if worker:
                            try:
                                worker.data_received.disconnect(mapper.handle_hid_data)
                            except Exception:
                                pass
                            try:
                                worker.error.disconnect(mapper.handle_error)
                            except Exception:
                                pass
                except Exception:
                    pass
                del self.mappers[path]

            try:
                self.hid_manager.stop_polling(path)
            except Exception:
                pass

    def _on_delete_requested(self, widget: EmuListItemWidget, item: QListWidgetItem):
        hid_emu = item.data(Qt.UserRole)
        if hid_emu:
            hid = hid_emu[0]
            device = self._find_device_by_display_name(hid)
            if device:
                path = device.get("path")
                if path in self.mappers:
                    mapper = self.mappers[path]
                    mapper.stop()
                    del self.mappers[path]
                try:
                    self.hid_manager.stop_polling(path)
                except Exception:
                    pass

        for i in range(self.emu_list.count()):
            if self.emu_list.item(i) is item:
                self.emu_list.takeItem(i)
                break

    def closeEvent(self, event):
        for path, mapper in list(self.mappers.items()):
            try:
                mapper.stop()
            except Exception:
                pass
            try:
                self.hid_manager.stop_polling(path)
            except Exception:
                pass
            del self.mappers[path]
        try:
            self.hid_manager.stop_all()
        except Exception:
            pass
        super().closeEvent(event)
