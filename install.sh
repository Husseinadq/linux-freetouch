#!/bin/bash

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (using sudo)"
  exit 1
fi

echo "🐧 Installing Linux Free Touch..."

# 1. Install OS dependencies
echo "➔ Installing python3-evdev..."
apt-get update -qq
apt-get install -y python3-evdev wget > /dev/null

# 2. Download the Python script directly to the binaries folder
echo "➔ Downloading freetouch daemon..."
wget -qO /usr/local/bin/linux-freetouch https://raw.githubusercontent.com/Husseinadq/linux-freetouch/main/freetouch.py
chmod +x /usr/local/bin/linux-freetouch

# 3. Download the systemd service file
echo "➔ Setting up background service..."
wget -qO /etc/systemd/system/freetouch.service https://raw.githubusercontent.com/Husseinadq/linux-freetouch/main/freetouch.service

# 4. Reload and start the daemon
systemctl daemon-reload
systemctl enable --now freetouch.service

echo "✅ Installation Complete! The daemon is now running in the background."
echo "Swipe the edges of your trackpad to test it."
