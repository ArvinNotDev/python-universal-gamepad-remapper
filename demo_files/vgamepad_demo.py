import core.hid_manager as hid_manager
import vgamepad as vg
import time

devices = hid_manager.enumerate()
for i, d in enumerate(devices):
    print(f"{i}: VID={d['vendor_id']:04X}, PID={d['product_id']:04X}, Name={d['product_string']}")


controller = hid_manager.device()
controller.open(vendor_id=1356, product_id=2508)

v_x360 = vg.VX360Gamepad()

print("Virtual Xbox controller ready. Press buttons on your DS4 to see mapping!")

try:
    while True:
        report = controller.read(64)
        if report:
            print(report[2])
            left_x = report[1]
            left_y = report[2]
            right_x = report[3]
            right_y = report[3]

            v_x360.left_joystick(x_value=left_x, y_value=left_y)
            v_x360.right_joystick(x_value=right_x, y_value=right_y)

            buttons = report[5]
            if buttons & 0x20:
                v_x360.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            else:
                v_x360.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)

            v_x360.update()


except KeyboardInterrupt:
    print("Exiting...")
