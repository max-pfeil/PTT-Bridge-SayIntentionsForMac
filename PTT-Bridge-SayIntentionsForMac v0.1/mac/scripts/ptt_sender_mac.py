#!/usr/bin/env python3
"""
PTT sender (macOS side).

First run: walks you through mapping HOTAS buttons to COM1, COM2,
Intercom 1, and Intercom 2, and saves the mapping next to this file.
Every later run reads that saved mapping and starts sending right away.

Run:
    python3 ptt_sender_mac.py
Re-run the setup wizard any time:
    python3 ptt_sender_mac.py --setup
"""

import json
import os
import socket
import sys
import time

import pygame

# --- config ---
HOST = "127.0.0.1"   # UTM forwards this host port into the VM
PORT = 49001
JOY_INDEX = 0         # which joystick (0 = first)
SEND_HZ = 100
# --------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "ptt_config.json")
CHANNELS = [(1, "COM1"), (2, "COM2"), (3, "Intercom 1"), (4, "Intercom 2")]


def get_joystick():
    pygame.init()
    pygame.joystick.init()
    if pygame.joystick.get_count() == 0:
        sys.exit("No joystick found. Connect your HOTAS and try again.")
    js = pygame.joystick.Joystick(JOY_INDEX)
    js.init()
    return js


def wait_for_button_press(js):
    """Block until a button is pressed, then released. Return its index."""
    prev = [False] * js.get_numbuttons()
    while True:
        pygame.event.pump()
        for i in range(js.get_numbuttons()):
            v = js.get_button(i)
            if v and not prev[i]:
                while js.get_button(i):  # wait for release (debounce)
                    pygame.event.pump()
                    time.sleep(0.01)
                return i
            prev[i] = v
        time.sleep(0.01)


def run_setup(js):
    print()
    print("=== HOTAS Setup ===")
    print(f"Detected: {js.get_name()}")
    print("For each function below, press the HOTAS button you want to use.\n")
    mapping = {}
    for channel, label in CHANNELS:
        print(f"Press the button for {label}...")
        btn = wait_for_button_press(js)
        print(f"  -> button {btn} assigned to {label}\n")
        mapping[str(btn)] = channel
    with open(CONFIG_PATH, "w") as f:
        json.dump(mapping, f, indent=2)
    print(f"Saved to {CONFIG_PATH}")
    print("Setup complete. Run the script again to start sending PTT.\n")


def load_config():
    with open(CONFIG_PATH) as f:
        raw = json.load(f)
    return {int(btn): channel for btn, channel in raw.items()}


def main():
    js = get_joystick()

    if "--setup" in sys.argv or not os.path.exists(CONFIG_PATH):
        run_setup(js)
        return

    button_map = load_config()
    names = {ch: label for ch, label in CHANNELS}
    print(f"Using: {js.get_name()}")
    print(f"Sending {button_map} -> {HOST}:{PORT}  (run with --setup to reconfigure)\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clock = pygame.time.Clock()
    last_state = {btn: False for btn in button_map}

    while True:
        pygame.event.pump()
        for btn, channel in button_map.items():
            pressed = bool(js.get_button(btn))
            if pressed != last_state[btn]:
                action = b"DOWN" if pressed else b"UP"
                sock.sendto(action + b":" + str(channel).encode(), (HOST, PORT))
                print(names.get(channel, channel), action.decode())
                last_state[btn] = pressed
        clock.tick(SEND_HZ)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
