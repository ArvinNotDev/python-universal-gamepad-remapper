import core.hid_manager as hid_manager
import time

for device in hid_manager.enumerate():
    print(device)
    print(type(device))
ds4 = hid_manager.device()
ds4.open(vendor_id=1356, product_id=2508)

while True:
    report = ds4.read(64)
    print(report)
    time.sleep(0.2)
