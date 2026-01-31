import pyautogui


class Mouse:
    @staticmethod
    def move(x: int, y: int, duration: float = 0.0):
        pyautogui.moveTo(x, y, duration=duration)

    @staticmethod
    def leftClick():
        pyautogui.click(button="left")

    @staticmethod
    def rightClick():
        pyautogui.click(button="right")
