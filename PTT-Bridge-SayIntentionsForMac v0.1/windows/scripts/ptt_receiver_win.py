"""
PTT receiver (Windows VM side) - virtual gamepad via ViGEmBus.

Requires (in the VM):
  1. ViGEmBus driver installed (ARM64 build):
     https://github.com/nefarius/ViGEmBus/releases
  2. x64 Python, then: pip install vgamepad

Creates a real virtual Xbox 360 controller and presses its buttons
based on UDP messages from the Mac. SI sees a genuine joystick
button - not synthetic keyboard input, which it filters out.

Run:
    python ptt_receiver_win.py
"""

import socket

import vgamepad as vg

PORT = 49001

# channel number -> Xbox controller button
BUTTON_MAP = {
    1: vg.XUSB_BUTTON.XUSB_GAMEPAD_A,  # COM1
    2: vg.XUSB_BUTTON.XUSB_GAMEPAD_B,  # COM2
    3: vg.XUSB_BUTTON.XUSB_GAMEPAD_X,  # Intercom 1
    4: vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,  # Intercom 2
}

gamepad = vg.VX360Gamepad()


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PORT))
    print(f"Listening on UDP {PORT}. Virtual Xbox 360 controller active.")

    down = {ch: False for ch in BUTTON_MAP}
    try:
        while True:
            data, _ = sock.recvfrom(64)
            try:
                action, channel_str = data.split(b":")
                channel = int(channel_str)
            except ValueError:
                continue
            btn = BUTTON_MAP.get(channel)
            if btn is None:
                continue
            if action == b"DOWN" and not down[channel]:
                gamepad.press_button(button=btn)
                gamepad.update()
                down[channel] = True
                print(f"channel {channel} DOWN")
            elif action == b"UP" and down[channel]:
                gamepad.release_button(button=btn)
                gamepad.update()
                down[channel] = False
                print(f"channel {channel} UP")
    except KeyboardInterrupt:
        for ch, is_down in down.items():
            if is_down:
                gamepad.release_button(button=BUTTON_MAP[ch])
        gamepad.update()


if __name__ == "__main__":
    main()
