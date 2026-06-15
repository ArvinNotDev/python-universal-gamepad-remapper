class controllerMonitor:

    @classmethod
    def monitor(cls, a, b, y, x, start, option, r3, l3, dpu, dpd, dpr, dpl, rb, lb, rt, lt, jlx, jly, jrx, jry):
        # Convert buttons to binary (1 = pressed, 0 = not pressed)
        buttons = [
            a, b, y, x,
            start, option,
            r3, l3,
            dpu, dpd, dpr, dpl,
            rb, lb
        ]

        binary = "".join("1" if bool(btn) else "0" for btn in buttons)

        return binary, rt, lt, jlx, jly, jrx, jry
