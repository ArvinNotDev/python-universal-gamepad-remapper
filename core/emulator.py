import vgamepad as vg

class EmulateX360:
    def __init__(self, device_path):
        self.device_path = device_path
        self.v_x360 = vg.VX360Gamepad()

    def update(self, ljx, ljy, rjx, rjy, a=False, x=False, b=False, y=False,
               rb=False, rt=0, lb=False, lt=0, dpu=False, dpd=False, dpr=False, dpl=False,
               back=False, start=False, l3=False, r3=False):

        # Joysticks
        self.v_x360.left_joystick(x_value=int(ljx), y_value=int(ljy))
        self.v_x360.right_joystick(x_value=int(rjx), y_value=int(rjy))

        # Triggers
        self.v_x360.left_trigger(value=int(lt))
        self.v_x360.right_trigger(value=int(rt))

        # Face Buttons
        self._press_release(a, vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        self._press_release(b, vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        self._press_release(x, vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        self._press_release(y, vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        
        # Shoulders
        self._press_release(lb, vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        self._press_release(rb, vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)

        # Menu / Stick Clicks
        self._press_release(back, vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK)
        self._press_release(start, vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
        self._press_release(l3, vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
        self._press_release(r3, vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB)

        # DPad simulation
        self._set_dpad(dpu, dpd, dpl, dpr)

        self.v_x360.update()

    def _press_release(self, pressed, button):
        if pressed:
            self.v_x360.press_button(button=button)
        else:
            self.v_x360.release_button(button=button)

    def _set_dpad(self, up, down, left, right):
        # Reset all D-pad buttons first
        self.v_x360.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        self.v_x360.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        self.v_x360.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
        self.v_x360.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)

        # Press based on state (allowing diagonals)
        if up:
            self.v_x360.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        if down:
            self.v_x360.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        if left:
            self.v_x360.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
        if right:
            self.v_x360.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)


class EmulateKeyboard:
    pass