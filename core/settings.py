import configparser

class SettingsManager:
    def __init__(self, path="config/settings.conf"):
        self.path = path
        self.config = configparser.ConfigParser()
        self.config.read(path)

    def get_device_section(self):
        return self.config["device"]

    def get_ui_section(self):
        return self.config["ui"]

    def get_developer_section(self):
        return self.config["developer"]

    def get_deadzones(self):
        left = self.config.getfloat("device", "left_stick_deadzone")
        right = self.config.getfloat("device", "right_stick_deadzone")
        return left, right

    def set_deadzone(self, left, right):
        self.config.set("device", "left_stick_deadzone", str(left))
        self.config.set("device", "right_stick_deadzone", str(right))

    def save(self):
        with open(self.path, "w") as f:
            self.config.write(f)