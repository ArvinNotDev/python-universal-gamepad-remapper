
import os
import uuid
import json
import socket
import threading
from math import sqrt, atan2, cos, sin

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

try:
    from plyer import accelerometer
except Exception:
    accelerometer = None


UUID_FILE = "gamepad_uuid.txt"
LAST_IP_FILE = "last_ip.txt"
NAME_FILE = "device_name.txt"

Window.clearcolor = (0.07, 0.09, 0.12, 1)


THEME = {
    "bg": (0.07, 0.09, 0.12, 1),
    "panel": (0.11, 0.13, 0.18, 1),
    "panel_alt": (0.13, 0.16, 0.22, 1),
    "border": (0.24, 0.30, 0.40, 1),
    "text": (0.95, 0.97, 1.00, 1),
    "muted": (0.70, 0.76, 0.85, 1),
    "subtle": (0.54, 0.60, 0.70, 1),
    "accent": (0.20, 0.58, 1.00, 1),
    "accent2": (0.96, 0.62, 0.18, 1),
    "success": (0.21, 0.72, 0.41, 1),
    "danger": (0.93, 0.30, 0.32, 1),
    "warn": (0.95, 0.74, 0.17, 1),
    "button": (0.18, 0.22, 0.30, 1),
    "button_down": (0.24, 0.30, 0.42, 1),
}


def clamp(value, lo, hi):
    return max(lo, min(hi, value))


def load_or_create_uuid():
    if os.path.exists(UUID_FILE):
        try:
            with open(UUID_FILE, "r", encoding="utf-8") as f:
                val = f.read().strip()
                if val:
                    return val
        except Exception:
            pass
    device_uuid = str(uuid.uuid4())
    try:
        with open(UUID_FILE, "w", encoding="utf-8") as f:
            f.write(device_uuid)
    except Exception:
        pass
    return device_uuid


def load_last_ip(default="192.168.1.100"):
    if os.path.exists(LAST_IP_FILE):
        try:
            with open(LAST_IP_FILE, "r", encoding="utf-8") as f:
                ip = f.read().strip()
                if ip:
                    return ip
        except Exception:
            pass
    return default


def save_last_ip(ip):
    try:
        with open(LAST_IP_FILE, "w", encoding="utf-8") as f:
            f.write(ip.strip())
    except Exception:
        pass


def load_name(default="KivyGamepad"):
    if os.path.exists(NAME_FILE):
        try:
            with open(NAME_FILE, "r", encoding="utf-8") as f:
                name = f.read().strip()
                if name:
                    return name
        except Exception:
            pass
    return default


def save_name(name):
    try:
        with open(NAME_FILE, "w", encoding="utf-8") as f:
            f.write(name.strip())
    except Exception:
        pass


class Card(BoxLayout):
    def __init__(self, **kwargs):
        padding = kwargs.pop("padding", (dp(12), dp(12), dp(12), dp(12)))
        spacing = kwargs.pop("spacing", dp(8))
        orientation = kwargs.pop("orientation", "vertical")
        self.radius = kwargs.pop("radius", dp(18))
        self.border_width = kwargs.pop("border_width", 1.0)
        self.fill_color = kwargs.pop("fill_color", THEME["panel"])
        self.border_color = kwargs.pop("border_color", THEME["border"])
        super().__init__(orientation=orientation, padding=padding, spacing=spacing, **kwargs)
        with self.canvas.before:
            Color(*self.fill_color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            Color(*self.border_color)
            self._line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius), width=self.border_width)
        self.bind(pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._line.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)


class SectionTitle(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("color", THEME["text"])
        kwargs.setdefault("bold", True)
        kwargs.setdefault("halign", "left")
        kwargs.setdefault("valign", "middle")
        kwargs.setdefault("text_size", (0, None))
        kwargs.setdefault("font_size", sp(17))
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(24))
        super().__init__(**kwargs)
        self.bind(size=self._update_text_size)

    def _update_text_size(self, *args):
        self.text_size = (self.width, None)


class Pill(Label):
    def __init__(self, **kwargs):
        kwargs.setdefault("color", THEME["text"])
        kwargs.setdefault("bold", True)
        kwargs.setdefault("font_size", sp(14))
        kwargs.setdefault("halign", "center")
        kwargs.setdefault("valign", "middle")
        super().__init__(**kwargs)
        self.padding = (dp(10), dp(6))
        self.size_hint = (None, None)
        self.bind(texture_size=self._fit)
        self._bg_color = THEME["button"]
        with self.canvas.before:
            Color(*self._bg_color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(999)])
        self.bind(pos=self._redraw, size=self._redraw)

    def set_color(self, color):
        self._bg_color = color
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self._bg_color)
            self._bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(999)])

    def _fit(self, *args):
        self.size = (self.texture_size[0] + dp(20), self.texture_size[1] + dp(12))

    def _redraw(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size


class Joystick(Widget):
    value_x = NumericProperty(128)
    value_y = NumericProperty(128)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.knob_radius_ratio = 0.34
        self.center_x_pos = 0
        self.center_y_pos = 0
        self.base_radius = 0
        self.knob_x = 0
        self.knob_y = 0
        self._touch_id = None

        with self.canvas:
            Color(0.10, 0.12, 0.16, 1)
            self.base_circle = Ellipse()
            Color(0.32, 0.38, 0.50, 1)
            self.base_line = Line(circle=(0, 0, 0), width=1.2)
            Color(0.18, 0.22, 0.30, 1)
            self.cross_x = Line(points=[], width=1)
            self.cross_y = Line(points=[], width=1)
            Color(0.20, 0.58, 1.00, 1)
            self.knob_circle = Ellipse()
            Color(1, 1, 1, 0.08)
            self.glow = Ellipse()

        self.bind(pos=self._update_graphics, size=self._update_graphics)
        self.bind(value_x=self._sync_from_values, value_y=self._sync_from_values)

    def _update_graphics(self, *args):
        diameter = min(self.width, self.height)
        self.base_radius = diameter / 2 * 0.93
        self.center_x_pos = self.x + self.width / 2
        self.center_y_pos = self.y + self.height / 2

        self.base_circle.pos = (
            self.center_x_pos - self.base_radius,
            self.center_y_pos - self.base_radius,
        )
        self.base_circle.size = (self.base_radius * 2, self.base_radius * 2)
        self.base_line.circle = (self.center_x_pos, self.center_y_pos, self.base_radius)

        self.cross_x.points = [
            self.center_x_pos - self.base_radius * 0.62, self.center_y_pos,
            self.center_x_pos + self.base_radius * 0.62, self.center_y_pos,
        ]
        self.cross_y.points = [
            self.center_x_pos, self.center_y_pos - self.base_radius * 0.62,
            self.center_x_pos, self.center_y_pos + self.base_radius * 0.62,
        ]

        self._sync_from_values()

    def _value_to_offset(self, value):
        return clamp((value - 128) / 127.0, -1.0, 1.0)

    def _offset_to_value(self, offset):
        return int(round(128 + clamp(offset, -1.0, 1.0) * 127))

    def _sync_from_values(self, *args):
        if self.base_radius <= 0:
            return

        nx = self._value_to_offset(self.value_x)
        ny = self._value_to_offset(self.value_y)
        self.knob_x = self.center_x_pos + nx * self.base_radius
        self.knob_y = self.center_y_pos - ny * self.base_radius

        knob_radius = self.base_radius * self.knob_radius_ratio
        self.knob_circle.pos = (
            self.knob_x - knob_radius,
            self.knob_y - knob_radius,
        )
        self.knob_circle.size = (knob_radius * 2, knob_radius * 2)

        glow_size = self.base_radius * 1.55
        self.glow.pos = (
            self.center_x_pos - glow_size / 2,
            self.center_y_pos - glow_size / 2,
        )
        self.glow.size = (glow_size, glow_size)

    def _set_knob(self, x, y):
        dx = x - self.center_x_pos
        dy = y - self.center_y_pos
        dist = sqrt(dx * dx + dy * dy)
        if dist > self.base_radius and dist > 0:
            angle = atan2(dy, dx)
            dx = cos(angle) * self.base_radius
            dy = sin(angle) * self.base_radius

        self.knob_x = self.center_x_pos + dx
        self.knob_y = self.center_y_pos + dy
        self.value_x = self._offset_to_value(dx / self.base_radius if self.base_radius else 0)
        self.value_y = self._offset_to_value(-(dy / self.base_radius if self.base_radius else 0))
        self._sync_from_values()

    def set_external_values(self, value_x=None, value_y=None):
        if self._touch_id is not None:
            return
        if value_x is not None:
            self.value_x = int(clamp(value_x, 0, 255))
        if value_y is not None:
            self.value_y = int(clamp(value_y, 0, 255))
        self._sync_from_values()

    def reset_to_center(self):
        self._touch_id = None
        self.value_x = 128
        self.value_y = 128
        self._sync_from_values()

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if self._touch_id is not None:
            return False
        self._touch_id = touch.uid
        self._set_knob(touch.x, touch.y)
        return True

    def on_touch_move(self, touch):
        if self._touch_id != touch.uid:
            return False
        self._set_knob(touch.x, touch.y)
        return True

    def on_touch_up(self, touch):
        if self._touch_id != touch.uid:
            return False
        self.reset_to_center()
        return True


class XboxClient(BoxLayout):
    mode = StringProperty("standard")
    gyro_enabled = BooleanProperty(False)
    connected = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(10), padding=dp(12), **kwargs)
        self.device_uuid = load_or_create_uuid()

        self.sock = None
        self._send_lock = threading.Lock()
        self._rx_stop = threading.Event()
        self._rx_thread = None
        self._gyro_poll_ev = None
        self._periodic_send_ev = None

        self.buttons = {
            "A": 0, "B": 0, "X": 0, "Y": 0,
            "LB": 0, "RB": 0, "BACK": 0, "START": 0, "GUIDE": 0,
            "L3": 0, "R3": 0,
            "DPAD_UP": 0, "DPAD_DOWN": 0, "DPAD_LEFT": 0, "DPAD_RIGHT": 0,
        }
        self.analog = {"L2": 0, "R2": 0}
        self.joystick = {"left_x": 128, "left_y": 128, "right_x": 128, "right_y": 128}

        self._gyro_supported = accelerometer is not None
        self._gyro_neutral = None
        self._gyro_steer = 0.0
        self._gyro_raw = 0.0
        self._gyro_last_sample = None

        self._build_ui()
        self._periodic_send_ev = Clock.schedule_interval(self.periodic_send, 0.10)
        self._gyro_poll_ev = Clock.schedule_interval(self._poll_gyro, 0.05)
        self._apply_mode_ui()

    # -------------------- UI --------------------
    def _build_ui(self):
        self.header = Card(size_hint_y=None, height=dp(88), spacing=dp(4), padding=(dp(16), dp(14), dp(16), dp(14)))
        title_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(28))
        title = Label(
            text="[b]Professional Gamepad[/b]",
            markup=True,
            color=THEME["text"],
            halign="left",
            valign="middle",
            font_size=sp(22),
        )
        title.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.connection_chip = Pill(text="Disconnected")
        self.connection_chip.set_color(THEME["danger"])
        title_row.add_widget(title)
        title_row.add_widget(self.connection_chip)

        subtitle = Label(
            text="Connect to your server, switch to driving mode, and use phone tilt for steering.",
            color=THEME["muted"],
            halign="left",
            valign="middle",
            font_size=sp(13),
        )
        subtitle.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.header.add_widget(title_row)
        self.header.add_widget(subtitle)
        self.add_widget(self.header)

        scroll = ScrollView(bar_width=0, do_scroll_x=False, do_scroll_y=True)
        content = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None)
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)

        # Connection card
        self.conn_card = Card(size_hint_y=None, height=dp(170), spacing=dp(8))
        self.conn_card.add_widget(SectionTitle(text="Connection"))
        self.conn_grid = GridLayout(cols=6, spacing=dp(8), size_hint_y=None, height=dp(82))

        self.name_input = self._make_text_input(load_name(), "Device name")
        self.ip_input = self._make_text_input(load_last_ip(), "Server IP")
        self.port_input = self._make_text_input("5000", "Port", input_filter="int")
        self.connect_btn = self._make_button("Connect", accent=THEME["accent"])
        self.connect_btn.bind(on_release=self.on_connect)
        self.status_label = Label(text="[color=9FB3CC]Ready[/color]", markup=True, color=THEME["text"], halign="left", valign="middle")
        self.status_label.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))

        self.conn_grid.add_widget(self._field_box("Name", self.name_input))
        self.conn_grid.add_widget(self._field_box("IP", self.ip_input))
        self.conn_grid.add_widget(self._field_box("Port", self.port_input))
        self.conn_grid.add_widget(self._field_box("", self.connect_btn, button=True))
        self.conn_grid.add_widget(self._field_box("Status", self.status_label))
        spacer = Widget()
        self.conn_grid.add_widget(spacer)
        self.conn_card.add_widget(self.conn_grid)

        self.auth_row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(42))
        self.code_input = self._make_text_input("", "Auth code", input_filter="int")
        self.submit_code_btn = self._make_button("Submit Code", accent=THEME["warn"])
        self.submit_code_btn.bind(on_release=self.on_submit_code)
        self.pair_status = Label(text="", color=THEME["subtle"], halign="left", valign="middle")
        self.pair_status.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.auth_row.add_widget(self._field_box("Auth", self.code_input))
        self.auth_row.add_widget(self._field_box("", self.submit_code_btn, button=True))
        self.auth_row.add_widget(self._field_box("", self.pair_status))
        self.conn_card.add_widget(self.auth_row)
        content.add_widget(self.conn_card)

        # Mode card
        self.mode_card = Card(size_hint_y=None, height=dp(182), spacing=dp(8))
        self.mode_card.add_widget(SectionTitle(text="Control Mode"))
        mode_row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(46))
        self.standard_mode_btn = self._make_button("Standard Mode", accent=THEME["accent"])
        self.driving_mode_btn = self._make_button("Driving Mode", accent=THEME["accent2"])
        self.standard_mode_btn.bind(on_release=lambda *_: self.set_mode("standard"))
        self.driving_mode_btn.bind(on_release=lambda *_: self.set_mode("driving"))
        mode_row.add_widget(self.standard_mode_btn)
        mode_row.add_widget(self.driving_mode_btn)
        self.mode_card.add_widget(mode_row)

        driving_row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(46))
        self.gyro_btn = self._make_button("Enable Gyro", accent=THEME["success"])
        self.gyro_btn.bind(on_release=self.toggle_gyro)
        self.calibrate_btn = self._make_button("Calibrate Tilt", accent=THEME["warn"])
        self.calibrate_btn.bind(on_release=self.calibrate_gyro)
        self.gyro_state = Label(text="Gyro: off", color=THEME["muted"], halign="left", valign="middle")
        self.gyro_state.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        driving_row.add_widget(self.gyro_btn)
        driving_row.add_widget(self.calibrate_btn)
        driving_row.add_widget(self.gyro_state)
        self.mode_card.add_widget(driving_row)

        sens_row = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None, height=dp(60))
        self.sensitivity_label = Label(text="Tilt sensitivity: 1.50x", color=THEME["muted"], halign="left", valign="middle", size_hint_y=None, height=dp(18))
        self.sensitivity_label.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.sensitivity_slider = Slider(min=0.5, max=3.0, value=1.5)
        self.sensitivity_slider.bind(value=self._on_sensitivity_change)
        sens_row.add_widget(self.sensitivity_label)
        sens_row.add_widget(self.sensitivity_slider)
        self.mode_card.add_widget(sens_row)

        steer_meter_row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(32))
        steer_text = Label(text="Steering", color=THEME["muted"], size_hint_x=0.18, halign="left", valign="middle")
        steer_text.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.steer_meter = Slider(min=-1, max=1, value=0, disabled=True, opacity=0.9)
        self.steer_value_label = Label(text="0.00", color=THEME["text"], size_hint_x=0.16, halign="right", valign="middle")
        self.steer_value_label.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        steer_meter_row.add_widget(steer_text)
        steer_meter_row.add_widget(self.steer_meter)
        steer_meter_row.add_widget(self.steer_value_label)
        self.mode_card.add_widget(steer_meter_row)

        content.add_widget(self.mode_card)

        # Main controls card
        self.controls_card = Card(spacing=dp(10), size_hint_y=None, height=dp(446))
        self.controls_card.add_widget(SectionTitle(text="Controller"))

        top_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(108))
        top_row.add_widget(self._build_trigger_cluster())
        top_row.add_widget(self._build_trigger_cluster(right=True))
        self.controls_card.add_widget(top_row)

        middle_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(292))

        self.left_panel = self._build_left_panel()
        self.center_panel = self._build_center_panel()
        self.right_panel = self._build_right_panel()

        middle_row.add_widget(self.left_panel)
        middle_row.add_widget(self.center_panel)
        middle_row.add_widget(self.right_panel)
        self.controls_card.add_widget(middle_row)

        content.add_widget(self.controls_card)

        self.driving_info = Card(size_hint_y=None, height=dp(112), spacing=dp(6))
        self.driving_info.add_widget(SectionTitle(text="Driving Mode Notes"))
        self.driving_note = Label(
            text="Enable Gyro to steer with the phone tilt. The left stick will mirror tilt on the X axis.",
            color=THEME["muted"],
            halign="left",
            valign="middle",
        )
        self.driving_note.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.driving_info.add_widget(self.driving_note)
        content.add_widget(self.driving_info)

        self.add_widget(scroll)

    def _make_text_input(self, text, hint, input_filter=None):
        ti = TextInput(
            text=text,
            hint_text=hint,
            multiline=False,
            input_filter=input_filter,
            padding=(dp(12), dp(10)),
            background_color=THEME["panel_alt"],
            foreground_color=THEME["text"],
            cursor_color=THEME["accent"],
            hint_text_color=THEME["subtle"],
            size_hint_y=None,
            height=dp(42),
        )
        return ti

    def _make_button(self, text, accent=None, font_size=sp(14), bold=True):
        btn = Button(
            text=text,
            background_normal="",
            background_down="",
            background_color=THEME["button"],
            color=THEME["text"],
            font_size=font_size,
            bold=bold,
            size_hint_y=None,
            height=dp(42),
        )
        btn._base_color = THEME["button"]
        btn._accent_color = accent if accent else THEME["button_down"]
        btn.bind(on_press=lambda inst: setattr(inst, "background_color", inst._accent_color))
        btn.bind(on_release=lambda inst: setattr(inst, "background_color", inst._base_color))
        return btn

    def _field_box(self, label_text, widget, button=False):
        box = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_x=1)
        if label_text:
            label = Label(text=label_text, color=THEME["subtle"], size_hint_y=None, height=dp(16), halign="left", valign="middle", font_size=sp(12))
            label.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
            box.add_widget(label)
        else:
            box.add_widget(Widget(size_hint_y=None, height=dp(16)))
        box.add_widget(widget)
        return box

    def _build_trigger_cluster(self, right=False):
        panel = Card(fill_color=THEME["panel_alt"])
        title = "Right Triggers" if right else "Left Triggers"
        panel.add_widget(SectionTitle(text=title))
        row = BoxLayout(orientation="horizontal", spacing=dp(10))
        if not right:
            self.btn_lb = self._make_button("LB", accent=THEME["button_down"])
            self.btn_lb.bind(on_press=lambda *_: self._momentary_button("LB", 1))
            self.btn_lb.bind(on_release=lambda *_: self._momentary_button("LB", 0))
            row.add_widget(self.btn_lb)

            self.lt_slider = Slider(min=0, max=255, value=0)
            self.lt_slider.bind(value=lambda inst, val: self._on_trigger_change("L2", val))
            row.add_widget(self._trigger_box("LT", self.lt_slider))
        else:
            self.rt_slider = Slider(min=0, max=255, value=0)
            self.rt_slider.bind(value=lambda inst, val: self._on_trigger_change("R2", val))
            row.add_widget(self._trigger_box("RT", self.rt_slider))

            self.btn_rb = self._make_button("RB", accent=THEME["button_down"])
            self.btn_rb.bind(on_press=lambda *_: self._momentary_button("RB", 1))
            self.btn_rb.bind(on_release=lambda *_: self._momentary_button("RB", 0))
            row.add_widget(self.btn_rb)
        panel.add_widget(row)
        return panel

    def _trigger_box(self, label, slider):
        box = BoxLayout(orientation="vertical", spacing=dp(4))
        label_widget = Label(text=label, color=THEME["muted"], size_hint_y=None, height=dp(18))
        label_widget.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        box.add_widget(label_widget)
        box.add_widget(slider)
        return box

    def _build_left_panel(self):
        panel = Card(fill_color=THEME["panel_alt"])
        panel.add_widget(SectionTitle(text="Left Side"))

        stick_wrap = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=0.56)
        self.left_stick_title = Label(text="Left Stick", color=THEME["muted"], size_hint_y=None, height=dp(18))
        self.left_stick_title.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.left_stick = Joystick(size_hint_y=1)
        self.left_stick.bind(value_x=self._on_left_stick_change, value_y=self._on_left_stick_change)
        self.btn_l3 = self._make_button("L3", accent=THEME["button_down"])
        self.btn_l3.bind(on_press=lambda *_: self._momentary_button("L3", 1))
        self.btn_l3.bind(on_release=lambda *_: self._momentary_button("L3", 0))
        stick_wrap.add_widget(self.left_stick_title)
        stick_wrap.add_widget(self.left_stick)
        stick_wrap.add_widget(self.btn_l3)

        dpad_wrap = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=0.44)
        dpad_title = Label(text="D-Pad", color=THEME["muted"], size_hint_y=None, height=dp(18))
        dpad_title.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        dpad_grid = GridLayout(cols=3, rows=3, spacing=dp(4))
        dpad_grid.add_widget(Widget())
        self.btn_dpad_up = self._make_button("▲", accent=THEME["button_down"], font_size=sp(16))
        self.btn_dpad_up.bind(on_press=lambda *_: self._momentary_button("DPAD_UP", 1))
        self.btn_dpad_up.bind(on_release=lambda *_: self._momentary_button("DPAD_UP", 0))
        dpad_grid.add_widget(self.btn_dpad_up)
        dpad_grid.add_widget(Widget())
        self.btn_dpad_left = self._make_button("◀", accent=THEME["button_down"], font_size=sp(16))
        self.btn_dpad_left.bind(on_press=lambda *_: self._momentary_button("DPAD_LEFT", 1))
        self.btn_dpad_left.bind(on_release=lambda *_: self._momentary_button("DPAD_LEFT", 0))
        dpad_grid.add_widget(self.btn_dpad_left)
        dpad_grid.add_widget(Widget())
        self.btn_dpad_right = self._make_button("▶", accent=THEME["button_down"], font_size=sp(16))
        self.btn_dpad_right.bind(on_press=lambda *_: self._momentary_button("DPAD_RIGHT", 1))
        self.btn_dpad_right.bind(on_release=lambda *_: self._momentary_button("DPAD_RIGHT", 0))
        dpad_grid.add_widget(self.btn_dpad_right)
        dpad_grid.add_widget(Widget())
        self.btn_dpad_down = self._make_button("▼", accent=THEME["button_down"], font_size=sp(16))
        self.btn_dpad_down.bind(on_press=lambda *_: self._momentary_button("DPAD_DOWN", 1))
        self.btn_dpad_down.bind(on_release=lambda *_: self._momentary_button("DPAD_DOWN", 0))
        dpad_grid.add_widget(self.btn_dpad_down)
        dpad_grid.add_widget(Widget())
        dpad_wrap.add_widget(dpad_title)
        dpad_wrap.add_widget(dpad_grid)

        panel.add_widget(stick_wrap)
        panel.add_widget(dpad_wrap)
        return panel

    def _build_center_panel(self):
        panel = Card(fill_color=THEME["panel_alt"])
        panel.add_widget(SectionTitle(text="System"))
        panel.add_widget(Widget())
        row = BoxLayout(orientation="horizontal", spacing=dp(8), size_hint_y=None, height=dp(52))
        self.btn_back = self._make_button("Back", accent=THEME["button_down"])
        self.btn_guide = self._make_button("Guide", accent=THEME["warn"])
        self.btn_start = self._make_button("Start", accent=THEME["button_down"])
        for name, btn in (("BACK", self.btn_back), ("GUIDE", self.btn_guide), ("START", self.btn_start)):
            btn.bind(on_press=lambda inst, n=name: self._momentary_button(n, 1))
            btn.bind(on_release=lambda inst, n=name: self._momentary_button(n, 0))
            row.add_widget(btn)
        panel.add_widget(row)
        panel.add_widget(Widget())
        return panel

    def _build_right_panel(self):
        panel = Card(fill_color=THEME["panel_alt"])
        panel.add_widget(SectionTitle(text="Right Side"))

        abxy_wrap = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=0.46)
        abxy_title = Label(text="Action Buttons", color=THEME["muted"], size_hint_y=None, height=dp(18))
        abxy_title.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        abxy_grid = GridLayout(cols=3, rows=3, spacing=dp(4))
        abxy_grid.add_widget(Widget())

        self.btn_y = self._make_button("Y", accent=(0.98, 0.84, 0.14, 1))
        self.btn_x = self._make_button("X", accent=(0.20, 0.52, 0.98, 1))
        self.btn_b = self._make_button("B", accent=(0.96, 0.28, 0.26, 1))
        self.btn_a = self._make_button("A", accent=(0.16, 0.80, 0.34, 1))

        for name, btn in (("Y", self.btn_y), ("X", self.btn_x), ("B", self.btn_b), ("A", self.btn_a)):
            btn.bind(on_press=lambda inst, n=name: self._momentary_button(n, 1))
            btn.bind(on_release=lambda inst, n=name: self._momentary_button(n, 0))

        abxy_grid.add_widget(self.btn_y)
        abxy_grid.add_widget(Widget())
        abxy_grid.add_widget(self.btn_x)
        abxy_grid.add_widget(Widget())
        abxy_grid.add_widget(self.btn_b)
        abxy_grid.add_widget(Widget())
        abxy_grid.add_widget(self.btn_a)
        abxy_grid.add_widget(Widget())
        abxy_wrap.add_widget(abxy_title)
        abxy_wrap.add_widget(abxy_grid)

        stick_wrap = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=0.54)
        stick_title = Label(text="Right Stick", color=THEME["muted"], size_hint_y=None, height=dp(18))
        stick_title.bind(size=lambda inst, *_: setattr(inst, "text_size", inst.size))
        self.right_stick = Joystick(size_hint_y=1)
        self.right_stick.bind(value_x=self._on_right_stick_change, value_y=self._on_right_stick_change)
        self.btn_r3 = self._make_button("R3", accent=THEME["button_down"])
        self.btn_r3.bind(on_press=lambda *_: self._momentary_button("R3", 1))
        self.btn_r3.bind(on_release=lambda *_: self._momentary_button("R3", 0))
        stick_wrap.add_widget(stick_title)
        stick_wrap.add_widget(self.right_stick)
        stick_wrap.add_widget(self.btn_r3)

        panel.add_widget(abxy_wrap)
        panel.add_widget(stick_wrap)
        return panel

    def _apply_mode_ui(self):
        if self.mode == "driving":
            self.standard_mode_btn.background_color = self.standard_mode_btn._base_color
            self.driving_mode_btn.background_color = self.driving_mode_btn._accent_color
            self.driving_info.opacity = 1
            self.driving_info.disabled = False
            self.driving_note.text = "Driving mode active. Enable Gyro to steer with phone tilt. The left stick follows the tilt X axis."
            self.left_stick_title.text = "Steering / Left Stick"
        else:
            self.standard_mode_btn.background_color = self.standard_mode_btn._accent_color
            self.driving_mode_btn.background_color = self.driving_mode_btn._base_color
            self.driving_info.opacity = 0.45
            self.driving_info.disabled = True
            self.left_stick_title.text = "Left Stick"
            self.driving_note.text = "Standard mode keeps the full controller layout with manual left and right sticks."
        self._update_gyro_ui()

    def _update_gyro_ui(self):
        if not self._gyro_supported:
            self.gyro_btn.text = "Gyro Unavailable"
            self.gyro_btn.disabled = True
            self.gyro_btn.background_color = THEME["button"]
            self.gyro_state.text = "Gyro: not supported on this device"
            self.gyro_state.color = THEME["subtle"]
            return

        self.gyro_btn.disabled = False
        if self.gyro_enabled:
            self.gyro_btn.text = "Disable Gyro"
            self.gyro_btn.background_color = self.gyro_btn._accent_color
            self.gyro_state.text = "Gyro: on"
            self.gyro_state.color = THEME["success"]
        else:
            self.gyro_btn.text = "Enable Gyro"
            self.gyro_btn.background_color = self.gyro_btn._base_color
            self.gyro_state.text = "Gyro: off"
            self.gyro_state.color = THEME["muted"]

    # -------------------- Actions --------------------
    def set_mode(self, mode):
        if mode not in ("standard", "driving"):
            return
        self.mode = mode
        self._apply_mode_ui()
        self.send_state()

    def toggle_gyro(self, *_):
        if not self._gyro_supported:
            self.show_status("Gyro not available")
            return
        self.gyro_enabled = not self.gyro_enabled
        if self.gyro_enabled and self._gyro_neutral is None:
            self.calibrate_gyro()
        self._update_gyro_ui()
        self.send_state()

    def calibrate_gyro(self, *_):
        if not self._gyro_supported:
            self.show_status("Gyro not available")
            return
        if self._gyro_last_sample is None:
            self.show_status("Move the phone slightly and try again")
            return
        self._gyro_neutral = self._gyro_last_sample[0]
        self._gyro_steer = 0.0
        self.steer_meter.value = 0
        self.steer_value_label.text = "0.00"
        self.show_status("Tilt calibrated")
        self.send_state()

    def _momentary_button(self, key, value):
        self.buttons[key] = value
        self.send_state()

    def _on_trigger_change(self, which, value):
        self.analog[which] = int(round(value))
        self.send_state()

    def _on_left_stick_change(self, *args):
        self.joystick["left_x"] = int(self.left_stick.value_x)
        self.joystick["left_y"] = int(self.left_stick.value_y)
        self.send_state()

    def _on_right_stick_change(self, *args):
        self.joystick["right_x"] = int(self.right_stick.value_x)
        self.joystick["right_y"] = int(self.right_stick.value_y)
        self.send_state()

    def _on_sensitivity_change(self, instance, value):
        self.sensitivity_label.text = f"Tilt sensitivity: {value:.2f}x"

    # -------------------- Networking --------------------
    def on_connect(self, *_):
        if self.connected:
            self.disconnect()
            return

        ip = self.ip_input.text.strip()
        port_text = self.port_input.text.strip()
        name = self.name_input.text.strip() or "KivyGamepad"

        if not ip or not port_text:
            self.show_status("IP and port are required")
            return

        try:
            port = int(port_text)
        except ValueError:
            self.show_status("Invalid port")
            return

        save_last_ip(ip)
        save_name(name)

        self.connect_btn.disabled = True
        self.connect_btn.text = "Connecting..."
        self.show_status("Connecting to server...")

        threading.Thread(target=self._connect_thread, args=(ip, port), daemon=True).start()

    def _connect_thread(self, ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.0)
            s.connect((ip, port))
            s.settimeout(1.0)

            self.sock = s
            self.connected = True
            self._rx_stop.clear()

            Clock.schedule_once(lambda dt: self._on_connected_ui(True), 0)

            self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
            self._rx_thread.start()

            self.send_state()

        except Exception:
            try:
                if self.sock:
                    self.sock.close()
            except Exception:
                pass
            self.sock = None
            self.connected = False
            Clock.schedule_once(lambda dt: self._on_connected_ui(False, "Connection failed"), 0)

    def _on_connected_ui(self, connected, message=None):
        self.connected = connected
        if connected:
            self.connection_chip.text = "Connected"
            self.connection_chip.set_color(THEME["success"])
            self.connect_btn.text = "Disconnect"
            self.connect_btn.disabled = False
            self.name_input.disabled = True
            self.show_status("Connected successfully")
        else:
            self.connection_chip.text = "Disconnected"
            self.connection_chip.set_color(THEME["danger"])
            self.connect_btn.text = "Connect"
            self.connect_btn.disabled = False
            self.name_input.disabled = False
            self.show_status(message or "Disconnected")
            self._stop_gyro_for_disconnect()

    def _stop_gyro_for_disconnect(self):
        self.gyro_enabled = False
        self._update_gyro_ui()
        if self._gyro_supported:
            try:
                accelerometer.disable()
            except Exception:
                pass

    def _rx_loop(self):
        try:
            while not self._rx_stop.is_set() and self.sock:
                try:
                    data = self.sock.recv(2048)
                    if not data:
                        break
                except socket.timeout:
                    continue
                except Exception:
                    break
        finally:
            Clock.schedule_once(lambda dt: self.disconnect(), 0)

    def on_submit_code(self, *_):
        code = (self.code_input.text or "").strip()
        if not code:
            self.show_pair_status("Enter a code first")
            return
        payload = self.build_state_message()
        payload["auth_code"] = code
        self._send(payload)
        self.code_input.text = ""
        self.show_pair_status("Sent")
        Clock.schedule_once(lambda dt: self.clear_pair_status(), 2.0)

    def clear_pair_status(self):
        self.pair_status.text = ""

    def show_pair_status(self, text):
        self.pair_status.text = text

    def show_status(self, text):
        self.status_label.text = f"[color=C9D4E2]{text}[/color]"

    def disconnect(self):
        self._rx_stop.set()
        self.connected = False
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        self.sock = None
        self._on_connected_ui(False, "Disconnected")

    def _send(self, obj):
        if not self.connected or not self.sock:
            return
        try:
            data = (json.dumps(obj) + "\n").encode("utf-8")
            with self._send_lock:
                self.sock.sendall(data)
        except Exception:
            self.disconnect()

    # -------------------- State --------------------
    def build_state_message(self):
        return {
            "uuid": self.device_uuid,
            "name": self.name_input.text.strip() or "UnknownDevice",
            "mode": self.mode,
            "gyro_enabled": self.gyro_enabled,
            "buttons": self.buttons,
            "analog": self.analog,
            "joystick": self.joystick,
            "tilt": {
                "neutral_x": self._gyro_neutral,
                "steer": round(self._gyro_steer, 4),
            },
        }

    def send_state(self):
        self._send(self.build_state_message())

    def periodic_send(self, dt):
        if self.connected:
            self.send_state()

    # -------------------- Gyro --------------------
    def _poll_gyro(self, dt):
        if not self._gyro_supported or not self.gyro_enabled or self.mode != "driving":
            return

        try:
            accelerometer.enable()
        except Exception:
            pass

        try:
            sample = accelerometer.acceleration
        except Exception:
            sample = None

        if not sample or len(sample) < 3:
            return

        x, y, z = sample
        if x is None or y is None or z is None:
            return

        self._gyro_last_sample = (float(x), float(y), float(z))

        if self._gyro_neutral is None:
            self._gyro_neutral = float(x)

        raw_delta = float(x) - float(self._gyro_neutral)
        sensitivity = float(self.sensitivity_slider.value)
        steer = clamp(raw_delta / (2.2 / sensitivity), -1.0, 1.0)

        # low-pass filter to keep the steering stable
        self._gyro_raw = steer
        self._gyro_steer = self._gyro_steer * 0.78 + steer * 0.22

        self.steer_meter.value = self._gyro_steer
        self.steer_value_label.text = f"{self._gyro_steer:+.2f}"
        self.gyro_state.text = f"Gyro: on | x={x:+.2f}"
        self.gyro_state.color = THEME["success"]

        # Mirror tilt into the left stick X axis
        steering_value = int(round(128 + self._gyro_steer * 127))
        self.left_stick.set_external_values(value_x=steering_value)
        self.joystick["left_x"] = steering_value

        # Keep the server updated without overwhelming it
        self.send_state()

    def on_stop(self):
        self._rx_stop.set()
        try:
            if self._gyro_supported:
                accelerometer.disable()
        except Exception:
            pass
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass


class XboxApp(App):
    def build(self):
        self.title = "Professional Gamepad"
        return XboxClient()

    def on_stop(self):
        if hasattr(self.root, "on_stop"):
            self.root.on_stop()


if __name__ == "__main__":
    XboxApp().run()
