import vgamepad as vg

class EmulateX360:
    v_x360 = vg.VX360Gamepad()

    def __init__(self, controller_uuid):
        self.update_controller = controller_uuid
        

    def update_controller(self, ljx, ljy, rjx, rjy, a, x, b, y, rb, rt, lb, lt, dpu, dpd, dpr, dpl):
        self.v_x360.left_joystick(x_value=int(ljx), y_value=int(ljy))
        self.v_x360.right_joystick(x_value=int(rjx), y_value=int(rjy))

        self.v_x360.left_trigger(value=int(lt))
        self.v_x360.right_trigger(value=int(rt))

        if a: self.v_x360.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        else: self.v_x360.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

        if b: self.v_x360.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
        else: self.v_x360.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)

        if x: self.v_x360.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
        else: self.v_x360.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_X)

        if y: self.v_x360.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
        else: self.v_x360.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)

        if lb: self.v_x360.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)
        else: self.v_x360.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER)

        if rb: self.v_x360.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
        else: self.v_x360.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)

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