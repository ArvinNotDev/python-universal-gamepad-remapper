import os

class ThemeManager:
    def __init__(self, app, base_path="ui/themes"):
        self.app = app
        self.base_path = base_path

    def apply_theme(self, theme_name: str):
        """theme_name is 'dark' or 'light'"""
        qss_path = os.path.join(self.base_path, f"{theme_name}.qss")

        if not os.path.exists(qss_path):
            print(f"[ThemeManager] Missing QSS file: {qss_path}")
            return

        with open(qss_path, "r", encoding="utf-8") as f:
            style = f.read()

        self.app.setStyleSheet(style)
