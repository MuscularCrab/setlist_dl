#!/usr/bin/env bash
# setlist-dl Linux launcher
# Passes all arguments through to the Python script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found."
    echo "  Ubuntu/Debian: sudo apt install python3"
    echo "  Arch/CachyOS:  sudo pacman -S python"
    exit 1
fi

python3 "$SCRIPT_DIR/setlist-dl.py" "$@"
