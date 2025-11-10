import weakref


class PlayerType:
    def __init__(self, type: str = None):
        self.type = type if type is not None else "CPU"

    def __repr__(self):
        return self.type


class ControllerRegistery:
    _controllers = weakref.WeakSet()

    @classmethod
    def register(cls, controller):
        cls._controllers.add(controller)
    
    @classmethod
    def get_all_controllers(cls):
        return list(cls._controllers)
    
    def get_controllers_length(cls):
        return len(cls._controllers)
    

class AddControllerName:
    def __init__(self, name: str = None):
        self.name = name if name is not None else f"player{ControllerRegistery.get_controllers_length()+1}"
    
    def __repr__(self):
        return self.name
    
class Controller:
    def __init__(self, device_id, name=None):
        self.name = AddControllerName(name)
        # i must implement this shit in the future
        