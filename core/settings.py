import configparser

class SettingsManager:
    def __init__(self, path="config/settings.conf"):
        self.config = configparser.ConfigParser()
        self.config.read(path)

    def get_device_section(self):
        return self.config["device"]

    def get_ui_section(self):
        return self.config["ui"]

    def get_developer_section(self):
        return self.config["developer"]

    def get_deadzone(self):
        left = self.config.getfloat("device", "left_stick_deadzone")
        right = self.config.getfloat("device", "right_stick_deadzone")
        return left, right
