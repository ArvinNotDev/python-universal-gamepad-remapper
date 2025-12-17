from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QFrame
)
from PySide6.QtCore import Qt


class SettingsPage(QWidget):
    def __init__(self, theme_manager, settings):
        super().__init__()
        self.settings = settings

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # ===== Title =====
        title = QLabel("Settings")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)

        # ===== Section =====
        section = QFrame()
        section.setFrameShape(QFrame.StyledPanel)
        section_layout = QVBoxLayout(section)
        section_layout.setSpacing(12)

        # ===== Left Joystick =====
        left_label = QLabel("Left joystick deadzone")
        section_layout.addWidget(left_label)

        left_row = QHBoxLayout()

        self.l_slider = QSlider(Qt.Horizontal)
        self.l_slider.setRange(0, 1000)

        self.l_value_label = QLabel()
        self.l_value_label.setFixedWidth(40)
        self.l_value_label.setAlignment(Qt.AlignRight)

        left_row.addWidget(self.l_slider)
        left_row.addWidget(self.l_value_label)

        section_layout.addLayout(left_row)

        # ===== Right Joystick =====
        right_label = QLabel("Right joystick deadzone")
        section_layout.addWidget(right_label)

        right_row = QHBoxLayout()

        self.r_slider = QSlider(Qt.Horizontal)
        self.r_slider.setRange(0, 1000)

        self.r_value_label = QLabel()
        self.r_value_label.setFixedWidth(40)
        self.r_value_label.setAlignment(Qt.AlignRight)

        right_row.addWidget(self.r_slider)
        right_row.addWidget(self.r_value_label)

        section_layout.addLayout(right_row)

        main_layout.addWidget(section)

        # ===== Buttons =====
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        default_btn = QPushButton("Restore Default")
        apply_btn = QPushButton("Apply")

        btn_layout.addWidget(default_btn)
        btn_layout.addWidget(apply_btn)
        main_layout.addLayout(btn_layout)

        # ===== Load from Config =====
        left, right = self.settings.get_deadzones()

        self.l_slider.setValue(int(left * 1000))
        self.r_slider.setValue(int(right * 1000))

        self.l_value_label.setText(f"{left:.2f}")
        self.r_value_label.setText(f"{right:.2f}")

        # ===== Connections =====
        self.l_slider.valueChanged.connect(self.on_left_changed)
        self.r_slider.valueChanged.connect(self.on_right_changed)

        default_btn.clicked.connect(self.restore_default)
        apply_btn.clicked.connect(self.apply_settings)

    # ===== Slots =====
    def on_left_changed(self, value):
        self.l_value_label.setText(f"{value / 1000.0:.2f}")

    def on_right_changed(self, value):
        self.r_value_label.setText(f"{value / 1000.0:.2f}")

    def restore_default(self):
        self.l_slider.setValue(500)
        self.r_slider.setValue(500)

    def apply_settings(self):
        left = self.l_slider.value() / 1000.0
        right = self.r_slider.value() / 1000.0

        self.settings.set_deadzone(left, right)
        self.settings.save()
