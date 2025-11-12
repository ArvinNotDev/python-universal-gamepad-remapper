import hid
import threading
import time

class HIDManager:
    def __init__(self, poll_interval=0.008):
        self.devices = []
        self._running = False
        self.poll_interval = poll_interval
        self._listeners = []

    def scan_devices(self):
        self.devices = hid.enumerate()
        return self.devices

    def start_polling(self, device_path):
        self._running = True
        t = threading.Thread(target=self._poll_device, args=(device_path,), daemon=True)
        t.start()

    def stop(self):
        self._running = False

    def add_listener(self, callback):
        self._listeners.append(callback)

    def _emit(self, data):
        for cb in self._listeners:
            cb(data)

    def _poll_device(self, path):
        with hid.Device(path=path) as dev:
            while self._running:
                try:
                    data = dev.read(64)
                    if data:
                        self._emit(data)
                except Exception as e:
                    print(f"HID poll error: {e}")
                    break
                time.sleep(self.poll_interval)
