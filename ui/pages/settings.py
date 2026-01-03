import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider,
    QFrame, QListWidget, QStackedWidget,
    QSpinBox, QCheckBox, QComboBox, QLineEdit, QMessageBox
)
from PySide6.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self, theme_manager, settings: object):
        super().__init__()
        self.theme_manager = theme_manager
        self.settings = settings

        root = QHBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        self.menu = QListWidget()
        self.menu.addItem("Device")
        self.menu.addItem("UI")
        self.menu.addItem("Developer")
        self.menu.setFixedWidth(140)
        root.addWidget(self.menu)

        self.pages = QStackedWidget()
        root.addWidget(self.pages)

        # ---------------- Device Page ----------------
        device_page = QWidget()
        device_layout = QVBoxLayout(device_page)
        device_layout.setContentsMargins(20, 20, 20, 20)
        device_layout.setSpacing(12)

        title = QLabel("Device Settings")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:16px; font-weight:600;")
        device_layout.addWidget(title)

        box = QFrame()
        box.setFrameShape(QFrame.StyledPanel)
        box.setStyleSheet("QFrame { padding: 12px; border-radius: 6px; }")
        box_layout = QVBoxLayout(box)
        box_layout.setSpacing(10)

        # polling rate
        lbl_poll = QLabel("Polling rate (Hz)")
        self.spin_poll = QSpinBox()
        self.spin_poll.setRange(0, 1000)
        self.spin_poll.setFixedWidth(100)
        pr_layout = QHBoxLayout()
        pr_layout.addWidget(lbl_poll)
        pr_layout.addStretch()
        pr_layout.addWidget(self.spin_poll)
        box_layout.addLayout(pr_layout)

        # auto reconnect
        self.chk_reconnect = QCheckBox("Auto reconnect")
        box_layout.addWidget(self.chk_reconnect)

        # dpad as mouse
        self.chk_dpad_mouse = QCheckBox("D-Pad as mouse")
        box_layout.addWidget(self.chk_dpad_mouse)

        # left deadzone
        lbl_left = QLabel("Left joystick deadzone")
        box_layout.addWidget(lbl_left)
        left_row = QHBoxLayout()
        self.left_slider = QSlider(Qt.Horizontal)
        self.left_slider.setRange(0, 1000)
        self.left_val = QLabel()
        self.left_val.setFixedWidth(46)
        self.left_val.setAlignment(Qt.AlignRight)
        left_row.addWidget(self.left_slider)
        left_row.addWidget(self.left_val)
        box_layout.addLayout(left_row)

        # right deadzone
        lbl_right = QLabel("Right joystick deadzone")
        box_layout.addWidget(lbl_right)
        right_row = QHBoxLayout()
        self.right_slider = QSlider(Qt.Horizontal)
        self.right_slider.setRange(0, 1000)
        self.right_val = QLabel()
        self.right_val.setFixedWidth(46)
        self.right_val.setAlignment(Qt.AlignRight)
        right_row.addWidget(self.right_slider)
        right_row.addWidget(self.right_val)
        box_layout.addLayout(right_row)

        device_layout.addWidget(box)

        device_buttons = QHBoxLayout()
        device_buttons.addStretch()
        self.dev_restore = QPushButton("Restore Default")
        self.dev_apply = QPushButton("Apply")
        self.dev_restore.setFixedWidth(140)
        self.dev_apply.setFixedWidth(100)
        device_buttons.addWidget(self.dev_restore)
        device_buttons.addWidget(self.dev_apply)
        device_layout.addLayout(device_buttons)

        self.pages.addWidget(device_page)

        # ---------------- UI Page ----------------
        ui_page = QWidget()
        ui_layout = QVBoxLayout(ui_page)
        ui_layout.setContentsMargins(20, 20, 20, 20)
        ui_layout.setSpacing(12)

        title_ui = QLabel("UI Settings")
        title_ui.setAlignment(Qt.AlignCenter)
        title_ui.setStyleSheet("font-size:16px; font-weight:600;")
        ui_layout.addWidget(title_ui)

        ui_box = QFrame()
        ui_box.setFrameShape(QFrame.StyledPanel)
        ui_box.setStyleSheet("QFrame { padding: 12px; border-radius: 6px; }")
        ui_box_layout = QVBoxLayout(ui_box)
        ui_box_layout.setSpacing(10)

        # language
        lbl_lang = QLabel("Language")
        self.combo_lang = QComboBox()
        self.combo_lang.addItems(["eng", "fa", "es"])
        self.combo_lang.setMinimumWidth(100)
        self.combo_lang.view().setMinimumWidth(130)
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(lbl_lang)
        lang_layout.addStretch()
        lang_layout.addWidget(self.combo_lang)
        ui_box_layout.addLayout(lang_layout)

        lbl_theme = QLabel("Theme")
        self.combo_theme = QComboBox()
        self.combo_theme.setMinimumWidth(100)
        self.combo_theme.view().setMinimumWidth(130)
        theme_names = []
        try:
            base = getattr(self.theme_manager, "base_path", None)
            if base and os.path.isdir(base):
                for f in os.listdir(base):
                    if f.endswith(".qss"):
                        theme_names.append(os.path.splitext(f)[0])
        except Exception:
            theme_names = []
        if not theme_names:
            theme_names = ["dark", "light"]
        self.combo_theme.addItems(theme_names)
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(lbl_theme)
        theme_layout.addStretch()
        theme_layout.addWidget(self.combo_theme)
        ui_box_layout.addLayout(theme_layout)

        ui_layout.addWidget(ui_box)

        ui_buttons = QHBoxLayout()
        ui_buttons.addStretch()
        self.ui_restore = QPushButton("Restore Default")
        self.ui_apply = QPushButton("Apply")
        self.ui_restore.setFixedWidth(140)
        self.ui_apply.setFixedWidth(100)
        ui_buttons.addWidget(self.ui_restore)
        ui_buttons.addWidget(self.ui_apply)
        ui_layout.addLayout(ui_buttons)

        self.pages.addWidget(ui_page)

        # ---------------- Developer Page ----------------
        dev_page = QWidget()
        dev_layout = QVBoxLayout(dev_page)
        dev_layout.setContentsMargins(20, 20, 20, 20)
        dev_layout.setSpacing(12)

        title_dev = QLabel("Developer Settings")
        title_dev.setAlignment(Qt.AlignCenter)
        title_dev.setStyleSheet("font-size:16px; font-weight:600;")
        dev_layout.addWidget(title_dev)

        dev_box = QFrame()
        dev_box.setFrameShape(QFrame.StyledPanel)
        dev_box.setStyleSheet("QFrame { padding: 12px; border-radius: 6px; }")
        dev_box_layout = QVBoxLayout(dev_box)
        dev_box_layout.setSpacing(10)

        self.chk_debug = QCheckBox("Debug")
        dev_box_layout.addWidget(self.chk_debug)

        self.chk_raw_hid = QCheckBox("Raw HID debug")
        dev_box_layout.addWidget(self.chk_raw_hid)

        self.chk_log_to_file = QCheckBox("Log to file")
        dev_box_layout.addWidget(self.chk_log_to_file)

        log_row = QHBoxLayout()
        lbl_path = QLabel("Log file path")
        self.edit_log_path = QLineEdit()
        self.edit_log_path.setFixedWidth(320)
        log_row.addWidget(lbl_path)
        log_row.addStretch()
        log_row.addWidget(self.edit_log_path)
        dev_box_layout.addLayout(log_row)

        dev_layout.addWidget(dev_box)

        dev_buttons = QHBoxLayout()
        dev_buttons.addStretch()
        self.dev_restore2 = QPushButton("Restore Default")
        self.dev_apply2 = QPushButton("Apply")
        self.dev_restore2.setFixedWidth(140)
        self.dev_apply2.setFixedWidth(100)
        dev_buttons.addWidget(self.dev_restore2)
        dev_buttons.addWidget(self.dev_apply2)
        dev_layout.addLayout(dev_buttons)

        self.pages.addWidget(dev_page)

        self.menu.currentRowChanged.connect(self.pages.setCurrentIndex)

        # ---------------- Load config values ----------------
        self.spin_poll.setValue(self.settings.get_polling_rate())
        self.chk_reconnect.setChecked(self.settings.get_auto_reconnect())
        self.chk_dpad_mouse.setChecked(self.settings.get_dpad_as_mouse())
        left, right = self.settings.get_deadzones()
        self.left_slider.setValue(int(left * 1000))
        self.right_slider.setValue(int(right * 1000))
        self.left_val.setText(f"{left:.2f}")
        self.right_val.setText(f"{right:.2f}")
        self.combo_lang.setCurrentText(self.settings.get_ui_language())
        current_theme = self.settings.get_ui_theme()
        if current_theme in [self.combo_theme.itemText(i) for i in range(self.combo_theme.count())]:
            self.combo_theme.setCurrentText(current_theme)
        self.chk_debug.setChecked(self.settings.get_developer_debug())
        self.chk_raw_hid.setChecked(self.settings.get_raw_hid_debug())
        self.chk_log_to_file.setChecked(self.settings.get_log_to_file())
        self.edit_log_path.setText(self.settings.get_log_file_path())

        # try apply theme using provided theme_manager
        try:
            self.theme_manager.apply_theme(self.settings.get_ui_theme())
        except Exception:
            pass

        # ---------------- Connections ----------------
        self.left_slider.valueChanged.connect(lambda v: self.left_val.setText(f"{v/1000:.2f}"))
        self.right_slider.valueChanged.connect(lambda v: self.right_val.setText(f"{v/1000:.2f}"))

        self.dev_restore.clicked.connect(self.restore_device_defaults)
        self.dev_apply.clicked.connect(self.apply_device)

        self.ui_restore.clicked.connect(self.restore_ui_defaults)
        self.ui_apply.clicked.connect(self.apply_ui)

        self.dev_restore2.clicked.connect(self.restore_dev_defaults)
        self.dev_apply2.clicked.connect(self.apply_dev)

    # ---------------- Device actions ----------------
    def restore_device_defaults(self):
        self.spin_poll.setValue(2)
        self.chk_reconnect.setChecked(False)
        self.chk_dpad_mouse.setChecked(True)
        self.left_slider.setValue(100)
        self.right_slider.setValue(100)
        self.left_val.setText("0.10")
        self.right_val.setText("0.10")

    def apply_device(self):
        old_polling = self.settings.get_polling_rate()
        polling = self.spin_poll.value()
        self.settings.set_polling_rate(polling)
        self.settings.set_auto_reconnect(self.chk_reconnect.isChecked())
        self.settings.set_dpad_as_mouse(self.chk_dpad_mouse.isChecked())
        left = self.left_slider.value() / 1000.0
        right = self.right_slider.value() / 1000.0
        self.settings.set_deadzones(left, right)
        self.settings.save()

        # Check if polling rate changed
        if polling != old_polling:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Restart Required")
            msg.setText("Polling rate has changed. Please restart the application for the changes to take effect.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

    # ---------------- UI actions ----------------
    def restore_ui_defaults(self):
        self.combo_lang.setCurrentText("eng")
        self.combo_theme.setCurrentText("dark")

    def apply_ui(self):
        self.settings.set_ui_language(self.combo_lang.currentText())
        theme = self.combo_theme.currentText()
        self.settings.set_ui_theme(theme)
        self.settings.save()
        try:
            self.theme_manager.apply_theme(theme)
        except Exception:
            pass

    # ---------------- Developer actions ----------------
    def restore_dev_defaults(self):
        self.chk_debug.setChecked(False)
        self.chk_raw_hid.setChecked(False)
        self.chk_log_to_file.setChecked(False)
        self.edit_log_path.setText("logs/mapper.log")

    def apply_dev(self):
        self.settings.set_developer_debug(self.chk_debug.isChecked())
        self.settings.set_raw_hid_debug(self.chk_raw_hid.isChecked())
        self.settings.set_log_to_file(self.chk_log_to_file.isChecked())
        self.settings.set_log_file_path(self.edit_log_path.text() or "logs/mapper.log")
        self.settings.save()
