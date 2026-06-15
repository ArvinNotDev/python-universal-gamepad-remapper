import os
import uuid
import json
import socket
import threading
from math import sqrt, atan2, cos, sin

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Ellipse, Line
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window

Window.size = (800, 480)

UUID_FILE = "gamepad_uuid.txt"
LAST_IP_FILE = "last_ip.txt"
NAME_FILE = "device_name.txt"


def load_or_create_uuid():
    if os.path.exists(UUID_FILE):
        with open(UUID_FILE, "r", encoding="utf-8") as f:
            val = f.read().strip()
            if val:
                return val
    device_uuid = str(uuid.uuid4())
    with open(UUID_FILE, "w", encoding="utf-8") as f:
        f.write(device_uuid)
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


class Joystick(Widget):
    value_x = NumericProperty(128)
    value_y = NumericProperty(128)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.knob_radius_ratio = 0.35
        self.center_x_pos = 0
        self.center_y_pos = 0
        self.base_radius = 0
        self.knob_x = 0
        self.knob_y = 0
        self._touch_id = None

        with self.canvas:
            self.base_color = Color(0.2, 0.2, 0.2, 1)
            self.base_circle = Ellipse()
            self.base_line_color = Color(0.8, 0.8, 0.8, 1)
            self.base_line = Line(circle=(0, 0, 0), width=1)
            self.knob_color = Color(0.1, 0.6, 1.0, 1)
            self.knob_circle = Ellipse()

        self.bind(pos=self._update_graphics, size=self._update_graphics)

    def _update_graphics(self, *args):
        diameter = min(self.width, self.height)
        self.base_radius = diameter / 2 * 0.95
        self.center_x_pos = self.x + self.width / 2
        self.center_y_pos = self.y + self.height / 2

        self.base_circle.pos = (
            self.center_x_pos - self.base_radius,
            self.center_y_pos - self.base_radius,
        )
        self.base_circle.size = (self.base_radius * 2, self.base_radius * 2)
        self.base_line.circle = (self.center_x_pos, self.center_y_pos, self.base_radius)

        knob_radius = self.base_radius * self.knob_radius_ratio

        if self._touch_id is None:
            if self.knob_x == 0 and self.knob_y == 0:
                self.knob_x = self.center_x_pos
                self.knob_y = self.center_y_pos

        self.knob_circle.pos = (
            self.knob_x - knob_radius,
            self.knob_y - knob_radius,
        )
        self.knob_circle.size = (knob_radius * 2, knob_radius * 2)

    def _set_knob(self, x, y):
        dx = x - self.center_x_pos
        dy = y - self.center_y_pos
        dist = sqrt(dx * dx + dy * dy)
        if dist > self.base_radius:
            angle = atan2(dy, dx)
            dx = cos(angle) * self.base_radius
            dy = sin(angle) * self.base_radius

        self.knob_x = self.center_x_pos + dx
        self.knob_y = self.center_y_pos + dy

        self._update_values_from_knob()
        self._update_graphics()

    def _update_values_from_knob(self):
        if self.base_radius == 0:
            nx = ny = 0
        else:
            nx = (self.knob_x - self.center_x_pos) / self.base_radius
            ny = (self.knob_y - self.center_y_pos) / self.base_radius

        nx = max(-1.0, min(1.0, nx))
        ny = max(-1.0, min(1.0, ny))

        def norm_to_byte(v):
            return int(round(128 + v * 127))

        self.value_x = norm_to_byte(nx)
        self.value_y = norm_to_byte(-ny)

    def reset_to_center(self):
        self._touch_id = None
        self.knob_x = self.center_x_pos
        self.knob_y = self.center_y_pos
        self.value_x = 128
        self.value_y = 128
        self._update_graphics()

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
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)
        self.device_uuid = load_or_create_uuid()

        # Networking
        self.sock = None
        self.connected = False

        # receiver thread control
        self._rx_stop = threading.Event()
        self._rx_thread = None

        # Buttons mapping
        self.buttons = {
            "A": 0, "B": 0, "X": 0, "Y": 0,
            "LB": 0, "RB": 0, "BACK": 0, "START": 0, "GUIDE": 0,
            "L3": 0, "R3": 0,
            "DPAD_UP": 0, "DPAD_DOWN": 0, "DPAD_LEFT": 0, "DPAD_RIGHT": 0,
        }
        self.analog = {"L2": 0, "R2": 0}
        self.joystick = {"left_x": 128, "left_y": 128, "right_x": 128, "right_y": 128}

        # ===== Connection bar =====
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=0.12, padding=dp(5), spacing=dp(5))
        conn_layout = BoxLayout(orientation="horizontal", size_hint_x=1.0, spacing=dp(5))
        
        # Name Input
        conn_layout.add_widget(Label(text="Name:", size_hint_x=0.08))
        self.name_input = TextInput(text=load_name(), multiline=False, size_hint_x=0.20)
        conn_layout.add_widget(self.name_input)

        # IP Input
        conn_layout.add_widget(Label(text="IP:", size_hint_x=0.05))
        self.ip_input = TextInput(text=load_last_ip(), multiline=False, size_hint_x=0.20)
        conn_layout.add_widget(self.ip_input)

        # Port Input
        conn_layout.add_widget(Label(text="Port:", size_hint_x=0.08))
        self.port_input = TextInput(text="5000", multiline=False, input_filter="int", size_hint_x=0.12)
        conn_layout.add_widget(self.port_input)

        self.connect_btn = Button(text="Connect", size_hint_x=0.12)
        self.connect_btn.bind(on_press=self.on_connect)
        conn_layout.add_widget(self.connect_btn)

        self.status_label = Label(text="Disconnected", size_hint_x=0.15)
        conn_layout.add_widget(self.status_label)

        top_bar.add_widget(conn_layout)
        self.add_widget(top_bar)

        # ===== Pairing UI (visible when connected in case auth is needed) =====
        self.pair_box = BoxLayout(orientation="horizontal", size_hint_y=0.10, padding=dp(5), spacing=dp(5))
        self.pair_label = Label(text="If server asks for Auth Code:", size_hint_x=0.45)
        self.code_input = TextInput(text="", multiline=False, input_filter="int", hint_text="4-digit code", size_hint_x=0.25)
        self.pair_btn = Button(text="Submit Auth Code", size_hint_x=0.2)
        self.pair_btn.bind(on_press=self.on_submit_code)
        self.pair_status = Label(text="", size_hint_x=0.10)

        self.pair_box.add_widget(self.pair_label)
        self.pair_box.add_widget(self.code_input)
        self.pair_box.add_widget(self.pair_btn)
        self.pair_box.add_widget(self.pair_status)
        self.pair_box.opacity = 0
        self.pair_box.disabled = True
        self.add_widget(self.pair_box)

        # ===== Controls UI =====
        top_row = BoxLayout(orientation="horizontal", size_hint_y=0.12, padding=dp(5), spacing=dp(10))

        lb_rb = BoxLayout(orientation="horizontal", size_hint_x=0.4, spacing=dp(5))
        self.btn_lb = self._make_push_button("LB")
        self.btn_rb = self._make_push_button("RB")
        lb_rb.add_widget(self.btn_lb)
        lb_rb.add_widget(self.btn_rb)
        top_row.add_widget(lb_rb)

        lt_rt = BoxLayout(orientation="horizontal", size_hint_x=0.6, spacing=dp(5), padding=dp(5))
        lt_box = BoxLayout(orientation="vertical")
        lt_box.add_widget(Label(text="LT", size_hint_y=0.3))
        self.lt_slider = Slider(min=0, max=255, value=0)
        self.lt_slider.bind(value=lambda inst, v: self._on_trigger_change("L2", v))
        lt_box.add_widget(self.lt_slider)

        rt_box = BoxLayout(orientation="vertical")
        rt_box.add_widget(Label(text="RT", size_hint_y=0.3))
        self.rt_slider = Slider(min=0, max=255, value=0)
        self.rt_slider.bind(value=lambda inst, v: self._on_trigger_change("R2", v))
        rt_box.add_widget(self.rt_slider)

        lt_rt.add_widget(lt_box)
        lt_rt.add_widget(rt_box)

        top_row.add_widget(lt_rt)
        self.add_widget(top_row)

        middle = BoxLayout(orientation="horizontal", size_hint_y=0.66, padding=dp(5), spacing=dp(10))

        left_side = BoxLayout(orientation="vertical", size_hint_x=0.35, spacing=dp(5))
        left_stick_box = BoxLayout(orientation="vertical", size_hint_y=0.5)
        left_stick_box.add_widget(Label(text="Left Stick", size_hint_y=0.15))
        self.left_stick = Joystick(size_hint_y=0.75)
        self.left_stick.bind(value_x=self._on_left_stick_change, value_y=self._on_left_stick_change)
        self.btn_l3 = self._make_push_button("L3", size_hint_y=0.1)

        left_stick_box.add_widget(self.left_stick)
        left_stick_box.add_widget(self.btn_l3)

        dpad_box = GridLayout(cols=3, rows=3, size_hint_y=0.5, padding=dp(5), spacing=dp(5))
        dpad_box.add_widget(Widget())
        self.btn_dpad_up = self._make_push_button("UP", key="DPAD_UP")
        dpad_box.add_widget(self.btn_dpad_up)
        dpad_box.add_widget(Widget())
        self.btn_dpad_left = self._make_push_button("LEFT", key="DPAD_LEFT")
        dpad_box.add_widget(self.btn_dpad_left)
        dpad_box.add_widget(Widget())
        self.btn_dpad_right = self._make_push_button("RIGHT", key="DPAD_RIGHT")
        dpad_box.add_widget(self.btn_dpad_right)
        dpad_box.add_widget(Widget())
        self.btn_dpad_down = self._make_push_button("DOWN", key="DPAD_DOWN")
        dpad_box.add_widget(self.btn_dpad_down)
        dpad_box.add_widget(Widget())

        left_side.add_widget(left_stick_box)
        left_side.add_widget(dpad_box)
        middle.add_widget(left_side)

        center_box = BoxLayout(orientation="vertical", size_hint_x=0.3, spacing=dp(5), padding=dp(5))
        center_box.add_widget(Widget(size_hint_y=0.4))
        center_buttons = BoxLayout(orientation="horizontal", size_hint_y=0.2, spacing=dp(5))
        self.btn_back = self._make_push_button("BACK")
        self.btn_guide = self._make_push_button("GUIDE", bg=(0.9, 0.9, 0.1, 1))
        self.btn_start = self._make_push_button("START")
        center_buttons.add_widget(self.btn_back)
        center_buttons.add_widget(self.btn_guide)
        center_buttons.add_widget(self.btn_start)
        center_box.add_widget(center_buttons)
        center_box.add_widget(Widget(size_hint_y=0.4))
        middle.add_widget(center_box)

        right_side = BoxLayout(orientation="vertical", size_hint_x=0.35, spacing=dp(5))
        abxy_grid = GridLayout(cols=3, rows=3, size_hint_y=0.5, padding=dp(5), spacing=dp(5))
        abxy_grid.add_widget(Widget())
        self.btn_y = self._make_push_button("Y", bg=(1, 1, 0, 1))
        abxy_grid.add_widget(self.btn_y)
        abxy_grid.add_widget(Widget())
        self.btn_x = self._make_push_button("X", bg=(0, 0.5, 1, 1))
        abxy_grid.add_widget(self.btn_x)
        abxy_grid.add_widget(Widget())
        self.btn_b = self._make_push_button("B", bg=(1, 0, 0, 1))
        abxy_grid.add_widget(self.btn_b)
        abxy_grid.add_widget(Widget())
        self.btn_a = self._make_push_button("A", bg=(0, 1, 0, 1))
        abxy_grid.add_widget(self.btn_a)
        abxy_grid.add_widget(Widget())

        right_stick_box = BoxLayout(orientation="vertical", size_hint_y=0.5)
        right_stick_box.add_widget(Label(text="Right Stick", size_hint_y=0.15))
        self.right_stick = Joystick(size_hint_y=0.75)
        self.right_stick.bind(value_x=self._on_right_stick_change, value_y=self._on_right_stick_change)
        self.btn_r3 = self._make_push_button("R3", size_hint_y=0.1)
        right_stick_box.add_widget(self.right_stick)
        right_stick_box.add_widget(self.btn_r3)

        right_side.add_widget(abxy_grid)
        right_side.add_widget(right_stick_box)
        middle.add_widget(right_side)

        self.add_widget(middle)

        # periodic send
        Clock.schedule_interval(self.periodic_send, 0.2)

        # initially disable controls
        self._set_controls_enabled(False)

    # ---------- UI helpers ----------
    def _set_controls_enabled(self, enabled: bool):
        def recurse(w):
            for child in getattr(w, "children", []):
                recurse(child)
            # don't disable these connection elements
            if w in (self.name_input, self.ip_input, self.port_input, self.connect_btn, self.code_input, self.pair_btn):
                return
            if isinstance(w, (Button, Slider, Joystick, TextInput)):
                w.disabled = not enabled

        recurse(self)

    def _show_pair_ui(self, show: bool, msg: str = ""):
        def _upd(_dt):
            self.pair_box.opacity = 1 if show else 0
            self.pair_box.disabled = not show
            if msg:
                self.pair_status.text = msg
        Clock.schedule_once(_upd, 0)

    def _clear_pair_status(self, dt):
        self.pair_status.text = ""

    # ---------- Button / Trigger helpers ----------
    def _make_push_button(self, label, key=None, size_hint_y=None, bg=None):
        if key is None:
            key = label
        if key not in self.buttons:
            self.buttons[key] = 0
        if bg is None:
            bg = (0.2, 0.2, 0.2, 1)

        btn = Button(text=label, background_color=bg,
                     size_hint_y=size_hint_y if size_hint_y is not None else 1)

        def on_down(instance):
            self.buttons[key] = 1
            instance.background_color = (0, 1, 0, 1)
            self.send_state()

        def on_up(instance):
            self.buttons[key] = 0
            instance.background_color = bg
            self.send_state()

        btn.bind(on_press=on_down)
        btn.bind(on_release=on_up)
        return btn

    def _on_trigger_change(self, which, value):
        self.analog[which] = int(value)
        self.send_state()

    def _on_left_stick_change(self, *args):
        self.joystick["left_x"] = int(self.left_stick.value_x)
        self.joystick["left_y"] = int(self.left_stick.value_y)
        self.send_state()

    def _on_right_stick_change(self, *args):
        self.joystick["right_x"] = int(self.right_stick.value_x)
        self.joystick["right_y"] = int(self.right_stick.value_y)
        self.send_state()

    # ---------- Networking ----------
    def on_connect(self, instance):
        if self.connected:
            self.disconnect()
            return

        ip = self.ip_input.text.strip()
        port_text = self.port_input.text.strip()
        name = self.name_input.text.strip() or "KivyGamepad"
        
        if not ip or not port_text:
            self.update_status("IP/Port missing")
            return

        try:
            port = int(port_text)
        except ValueError:
            self.update_status("Invalid port")
            return

        save_last_ip(ip)
        save_name(name)

        self.update_status("Connecting...")
        self.connect_btn.text = "Connecting..."
        self.connect_btn.disabled = True

        threading.Thread(target=self._connect_thread, args=(ip, port), daemon=True).start()

    def _connect_thread(self, ip, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5.0)
            s.connect((ip, port))
            s.settimeout(None)

            self.sock = s
            self.connected = True
            self._rx_stop.clear()

            self._set_connected_ui(True)
            self._set_controls_enabled(True)
            # Show the pairing UI just in case it's a new connection
            self._show_pair_ui(True, "")

            # start receiver (mainly to detect socket close)
            self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
            self._rx_thread.start()

            # force sending initial state immediately to trigger server checks
            self.send_state()

        except Exception as e:
            self.sock = None
            self.connected = False
            self._set_connected_ui(False)
            self.update_status("Conn Failed")

    def _rx_loop(self):
        try:
            while not self._rx_stop.is_set() and self.sock:
                data = self.sock.recv(2048)
                # If recv unblocks with no data, connection closed
                if not data:
                    break
        except Exception:
            pass
        finally:
            Clock.schedule_once(lambda dt: self.disconnect(), 0)

    def on_submit_code(self, instance):
        code = (self.code_input.text or "").strip()
        if not code:
            self._show_pair_ui(True, "Enter code")
            return
        
        # Inject the auth_code into the message
        msg = self.build_state_message()
        msg["auth_code"] = code
        self._send(msg)
        
        self.code_input.text = ""
        self.pair_status.text = "Sent!"
        Clock.schedule_once(self._clear_pair_status, 3)

    def _send(self, obj: dict):
        if not self.connected or not self.sock:
            return
        data = json.dumps(obj) + "\n"
        try:
            self.sock.sendall(data.encode("utf-8"))
        except Exception as e:
            self.update_status("Send error")
            self.disconnect()

    def _set_connected_ui(self, is_connected):
        def _update(_dt):
            if is_connected:
                self.status_label.text = "Connected"
                self.connect_btn.text = "Disconnect"
                self.name_input.disabled = True
            else:
                self.status_label.text = "Disconnected"
                self.connect_btn.text = "Connect"
                self.name_input.disabled = False
            self.connect_btn.disabled = False
        Clock.schedule_once(_update, 0)

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.status_label, "text", text), 0)

    def disconnect(self):
        self._rx_stop.set()
        self.connected = False
        if self.sock:
            try:
                self.sock.close()
            except OSError:
                pass
        self.sock = None
        self._set_connected_ui(False)
        self._set_controls_enabled(False)
        self._show_pair_ui(False)

    # ---------- State sending ----------
    def build_state_message(self):
        return {
            "uuid": self.device_uuid,
            "name": self.name_input.text.strip() or "UnknownDevice",
            "buttons": self.buttons,
            "analog": self.analog,
            "joystick": self.joystick,
        }

    def send_state(self):
        if not self.connected or not self.sock:
            return
        self._send(self.build_state_message())

    def periodic_send(self, dt):
        self.send_state()


class XboxApp(App):
    def build(self):
        return XboxClient()


if __name__ == "__main__":
    XboxApp().run()
