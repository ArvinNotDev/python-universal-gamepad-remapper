class PlayerType:
    def __init__(self, type: str = None):
        self.type = type if type else "CPU"

    def __repr__(self):
        return self.type


class Controller:
    """
    Represents a physical controller.
    Unique ID is now the device path.
    """

    def __init__(self, vendor_id, product_id, device_path, name=None):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device_path = device_path
        self.name = name if name else f"Controller-{vendor_id:04X}:{product_id:04X}"

    @property
    def unique_id(self):
        """Unique ID string based on VID:PID:path (optional, can just use path)"""
        return self.device_path

    def __repr__(self):
        return f"<Controller {self.name} ({self.vendor_id:04X}:{self.product_id:04X})>"
