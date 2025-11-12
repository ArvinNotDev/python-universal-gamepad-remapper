import vgamepad as vg

class EmulateX360:
    def __init__(self, controller_uuid):
        self.controller_uuid = controller_uuid
        self.v_x360 = vg.VX360Gamepad()

    def update(self, ljx, ljy, rjx, rjy, a=False, x=False, b=False, y=False,
               rb=False, rt=0, lb=False, lt=0, dpu=False, dpd=False, dpr=False, dpl=False):

        # Joysticks
        self.v_x360.left_joystick(x_value=int(ljx), y_value=int(ljy))
        self.v_x360.right_joystick(x_value=int(rjx), y_value=int(rjy))

        # Triggers
        self.v_x360.left_trigger(value=int(lt))
        self.v_x360.right_trigger(value=int(rt))

        # Buttons
        self._press_release(a, vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        self._press_release(b, vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        self._press_release(x, vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        self._press_release(y, vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        self._press_release(lb, vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        self._press_release(rb, vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)

        # DPad
        if dpu:
            self.v_x360.directional_pad(direction=vg.DPAD_UP)
        elif dpd:
            self.v_x360.directional_pad(direction=vg.DPAD_DOWN)
        elif dpl:
            self.v_x360.directional_pad(direction=vg.DPAD_LEFT)
        elif dpr:
            self.v_x360.directional_pad(direction=vg.DPAD_RIGHT)
        else:
            self.v_x360.directional_pad(direction=vg.DPAD_NONE)

        self.v_x360.update()

    def _press_release(self, pressed, button):
        if pressed:
            self.v_x360.press_button(button=button)
        else:
            self.v_x360.release_button(button=button)
