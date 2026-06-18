# HOTAS PTT Bridge for SayIntentions (UTM / Windows ARM VM)
Original: https://github.com/max-pfeil/PTT-Bridge-SayIntentionsForMac/

> **Disclaimer:** I'm not a programmer. This project was built through a chat
> with Claude (Anthropic's AI assistant), which wrote and debugged the code
> based on my requirements and testing feedback. Use at your own discretion —
> issues and pull requests are welcome, but I may not be able to debug
> code-level problems myself.

Lets one physical HOTAS control PTT in SayIntentions (running in a UTM Windows
ARM VM) while staying fully usable for flying X-Plane on the Mac.

## How it works

```
HOTAS (USB, stays on Mac)
   |
   v
ptt_sender_mac.py   (reads HOTAS buttons)
   |  UDP  "DOWN:<channel>" / "UP:<channel>"
   v  (via UTM port-forward)
ptt_receiver_win.py (inside the VM, creates a virtual gamepad)
   |
   v
Virtual Xbox 360 Controller
   |
   v
SayIntentions (binds COM1/COM2/Intercom1/Intercom2 to A/B/X/Y)
```

The HOTAS is never passed through to the VM — only button presses/releases
cross over as small UDP packets.

## Requirements

**Mac:**
- Homebrew
- SDL2 (`sdl2`, `sdl2_image`, `sdl2_mixer`, `sdl2_ttf`, `sdl2_gfx`, `pkg-config`)
- Python 3 with `pygame`

**Windows VM (UTM, ARM64 Windows 11):**
- [ViGEmBus driver](https://github.com/nefarius/ViGEmBus/releases) — installer
  with `arm64` in the filename
- **64-bit (x64) Python**, not the ARM64-native build
- `pip install vgamepad`

**UTM:**
- Network mode: `Emulated VLAN`
- Port forwarding: UDP, host port `49001` → guest port `49001`

## One-time steps that can't be automated

- **UTM port forward** is host-app specific and must be set by hand: VM
  Settings → Network → Port Forwarding → add `UDP`, Host Port `49001`, Guest
  Port `49001`.
- **ViGEmBus driver install** requires an admin confirmation click on Windows
  (a kernel driver, can't be silently scripted). Download from the link above,
  pick the installer with `arm64` in the filename, and run it. If Windows
  Defender blocks it mid-install, temporarily disable real-time protection,
  install, then re-enable it. **Reboot the VM afterward.**

## Setup

1. **Mac dependencies:**
   ```
   brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf sdl2_gfx pkg-config
   pip3 install --break-system-packages pygame
   ```

2. **Windows Python + vgamepad:** install 64-bit Python from python.org, then:
   ```
   pip install vgamepad
   ```

3. **Find your HOTAS button indices** (Mac):
   ```
   python3 ptt_sender_mac.py --scan
   ```
   Press each button you want to use and note the printed index. Edit
   `BUTTON_MAP` in `ptt_sender_mac.py` to match:
   ```python
   BUTTON_MAP = {
       4: 1,  # COM1
       5: 2,  # COM2
       6: 3,  # Intercom 1
       7: 4,  # Intercom 2
   }
   ```

## Running it

**Windows VM** (as Administrator — needed to create the virtual gamepad):
```
python ptt_receiver_win.py
```
or double-click `start_ptt_receiver.bat`. Should print
`Listening on UDP 49001. Virtual Xbox 360 controller active.`

**Mac:**
```
python3 ptt_sender_mac.py
```
or double-click `start_ptt_sender.command` (first run: right-click → Open, to
clear macOS's Gatekeeper quarantine flag).

Confirm in Windows Device Manager that a new **Xbox 360 Controller** appears
while the receiver is running.

## Bind the controls in SayIntentions

With the receiver running, start binding each control one at a time and press
the matching HOTAS button:

- COM1 → Xbox button **A**
- COM2 → Xbox button **B**
- Intercom 1 → Xbox button **X**
- Intercom 2 → Xbox button **Y**

## Troubleshooting

- **`ModuleNotFoundError: No module named 'pygame'`** — pygame isn't installed,
  see Setup step 1.
- **pygame build fails with `'SDL.h' file not found`** — install SDL2 via
  Homebrew before retrying pip.
- **ViGEmBus installer seems to cancel itself mid-install** — almost always
  Windows Defender blocking it silently; disable real-time protection
  temporarily, then re-enable after install.
- **No Xbox 360 Controller appears after running the receiver** — confirm
  you're running 64-bit (not ARM64) Python in the VM, and that ViGEmBus shows
  up under Device Manager → System devices.
- **SayIntentions doesn't react to a real keypress sent from a script** —
  expected; SI filters synthetic/injected keyboard input. That's exactly why
  this uses a virtual gamepad (ViGEmBus) instead of keystrokes.
- **Mac `.command` file: "couldn't be executed because you don't have the
  necessary permissions"** — run `chmod +x start_ptt_sender.command` once, or
  right-click → Open instead of double-clicking.
