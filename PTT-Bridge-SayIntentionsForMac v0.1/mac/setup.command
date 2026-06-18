#!/bin/bash
# One-time dependency setup (Mac side).
# Double-click in Finder, or run: bash setup.command

set -e

if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found. Installing Homebrew (you may be asked for your password)..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

echo "Installing SDL2 libraries..."
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf sdl2_gfx pkg-config

echo "Installing pygame..."
pip3 install --break-system-packages pygame

echo
echo "Setup complete."
echo "Next: double-click start_ptt_sender.command to begin."
read -p "Press Enter to close..."
