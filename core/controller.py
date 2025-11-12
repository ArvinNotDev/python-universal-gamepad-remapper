import weakref
import uuid


class PlayerType:
    def __init__(self, type: str = None):
        self.type = type if type else "CPU"

    def __repr__(self):
        return self.type


class ControllerRegistry:
    _controllers = weakref.WeakSet()

    @classmethod
    def register(cls, controller):
        cls._controllers.add(controller)

    @classmethod
    def get_all_controllers(cls):
        return list(cls._controllers)

    @classmethod
    def get_controllers_length(cls):
        return len(cls._controllers)


class AddControllerName:
    def __init__(self, name: str = None):
        self.name = name if name else f"player{ControllerRegistry.get_controllers_length() + 1}"

    def __repr__(self):
        return self.name


class Controller:
    """Represents a physical controller device."""
    def __init__(self, vendor_id, product_id, name=None, path=None):
        self.uuid = uuid.uuid4()
        self.name = AddControllerName(name)
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.path = path  # HID device path

        ControllerRegistry.register(self)

    def __repr__(self):
        return f"{self.name} ({self.vendor_id:04X}:{self.product_id:04X})"
