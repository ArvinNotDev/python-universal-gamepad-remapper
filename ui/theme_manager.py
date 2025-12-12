import os

class ThemeManager:
    def __init__(self, app, base_path="ui/themes"):
        self.app = app
        self.base_path = base_path
        self._cache = {}

    def apply_theme(self, theme_name: str):
        base_qss = self._read(os.path.join(self.base_path, f"{theme_name}.qss"))
        self.base_qss = base_qss
        self.current_theme = theme_name
        self.app.setStyleSheet(self.base_qss)

    def apply_component(self, component_name: str):
        """Append a component QSS (e.g. 'dashboard') to base and apply."""
        comp_path = os.path.join(self.base_path, "components", f"{component_name}.qss")
        comp_qss = self._read(comp_path)
        composed = (self.base_qss or "") + "\n\n" + (comp_qss or "")
        self.app.setStyleSheet(composed)

    def clear_component(self):
        """Revert to base theme only."""
        self.app.setStyleSheet(self.base_qss or "")
        
    def _read(self, path):
        if path in self._cache:
            return self._cache[path]
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read()
        self._cache[path] = txt
        return txt