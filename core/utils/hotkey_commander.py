import subprocess
from typing import Iterable, Dict, Optional, Tuple

import keyboard


class HotkeyCommander:
    """
    Executes either:
      - Built-in media functions via `keyboard.send`
      - Custom shell commands via `subprocess.run`

    media_functions: dict mapping logical names -> keyboard keys.
        Example:
            {
                "volume up": "volume up",
                "volume down": "volume down",
                "play/pause media": "play/pause media",
                "next track": "next track",
                "previous track": "previous track",
                "volume mute": "volume mute",
            }

    custom_commands: dict mapping logical names -> shell commands.
        Example:
            {
                "open_notepad": "notepad.exe",
                "restart_explorer": "taskkill /f /im explorer.exe & start explorer.exe",
            }

    Usage:
        commander = HotkeyCommander(media_functions, custom_commands)
        commander.do("volume up", is_custom_command=False)
        commander.do("open_notepad", is_custom_command=True)
    """

    def __init__(
        self,
        media_functions: Dict[str, str],
        custom_commands: Optional[Dict[str, str]] = None,
        default_working_dir: Optional[str] = None,
    ):
        self.media_controls = keyboard
        self.media_functions = media_functions
        self.custom_commands = custom_commands or {}
        self.default_working_dir = default_working_dir

    def do(self, function: str, is_custom_command: bool) -> Tuple[bool, str]:
        """
        Execute the given function.

        If is_custom_command is False:
            - Treat `function` as a media function name and send a key via `keyboard.send`.

        If is_custom_command is True:
            - Treat `function` as a key in `self.custom_commands` and
              execute the mapped shell command via `subprocess.run`.

        Returns:
            (ok, message)
        """

        # Media hotkey (volume up / play-pause / etc.)
        if not is_custom_command:
            if function not in self.media_functions:
                return False, f"Unknown media function '{function}'."

            key = self.media_functions[function]
            try:
                self.media_controls.send(key)
                return True, f"Media function executed: {function} (sent '{key}')."
            except Exception as e:
                return False, f"Failed to send media key '{key}': {e}"

        # Custom shell command
        if is_custom_command:
            if function not in self.custom_commands:
                return False, f"Unknown custom command key '{function}'."

            command = self.custom_commands[function]
            try:
                # shell=True so you can use things like "dir & echo hi" (Windows) or "ls && echo hi" (Linux/macOS)
                completed = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.default_working_dir,
                    capture_output=True,
                    text=True,
                )

                if completed.returncode == 0:
                    return True, f"Custom command '{function}' executed successfully."
                else:
                    return (
                        False,
                        f"Command '{function}' failed with code {completed.returncode}.\n"
                        f"stdout:\n{completed.stdout}\n\nstderr:\n{completed.stderr}",
                    )
            except Exception as e:
                return False, f"Failed to execute custom command '{function}': {e}"

        # Should never get here
        return False, "Invalid usage of HotkeyCommander.do(...)"
