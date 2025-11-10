import hid

class Hid:
    devices = []

    def update_devices(self):
        for device in hid.enumerate():
            self.devices.append(device)
    
    def get_specific_device_details(self, vendor=None, device_id=None, path=None):
        if vendor:
            pass

        if device_id:
            pass

        if path:
            pass

        return None

    def list_devices(self):
        return self.devices