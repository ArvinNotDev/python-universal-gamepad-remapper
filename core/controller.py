import uuid


class PlayerType:
    def __init__(self, type: str = None):
        self.type = type if type is not None else "CPU"

    def __repr__(self):
        return self.type


class Controller:
    """
    Represents a physical controller.
    Unique ID is generated from vendor_id, product_id, and path.
    """

    def __init__(self, vendor_id, product_id, device_path, name=None):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device_path = device_path
        self.name = name if name else f"Controller-{vendor_id:04X}:{product_id:04X}"
        self.uuid = uuid.uuid4()

    @property
    def unique_id(self):
        """Unique ID string based on VID:PID:path"""
        return f"{self.vendor_id:04X}:{self.product_id:04X}:{self.device_path}"

    def __repr__(self):
        return f"<Controller {self.name} ({self.unique_id})>"
