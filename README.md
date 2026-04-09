# 🐧 Linux Free Touch

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)]()

**A universal, open-source user-space daemon that enables native edge-swipe gestures (Volume & Brightness) on Linux trackpads.**

Originally built to restore the **Huawei Free Touch** features on MateBook laptops running Ubuntu/Linux, this tool dynamically calibrates to work on almost any modern laptop trackpad (Dell, Lenovo, HP, Asus, etc.) that supports multi-touch hardware.

---

## 🔍 The Problem It Solves
On Windows, laptops like the Huawei MateBook X Pro use a proprietary background service to detect when your finger slides along the extreme edges of the trackpad, allowing you to change volume and brightness. On Linux, standard drivers (`libinput` / `synaptics`) treat the entire pad as a standard mouse, meaning you lose these premium hardware features.

**Linux Free Touch** safely intercepts the raw hardware coordinate data via `evdev`, bypasses audio server permission issues by injecting virtual media keystrokes, and restores your hardware gestures natively.

## ✨ Features
* 🔊 **Right Edge Swipe:** Smoothly adjust system Volume up/down.
* ☀️ **Left Edge Swipe:** Smoothly adjust screen Brightness up/down.
* ✋ **Hardware Palm Rejection:** Intelligently ignores large surface touches so your palm doesn't accidentally trigger volume changes while typing.
* 📐 **Dynamic Hardware Calibration:** Automatically calculates your specific trackpad's physical dimensions (X/Y axis maximums) to map the edges perfectly, regardless of your laptop's make or model.
* 🪶 **Ultra-Lightweight:** Written in pure Python, running as an invisible `systemd` background service with virtually zero CPU overhead.

---

## 🚀 Installation

### Method 1: Quick Install (Recommended)
You can install the dependencies, download the binary, and start the background service with a single command. Open your terminal and run:

```bash
wget -qO- https://raw.githubusercontent.com/Husseinadq/linux-freetouch/main/install.sh | sudo bash
```

### Method 2: Manual Installation
If you prefer to audit the installation steps yourself, you can install the tool manually.

**1. Install System Dependencies**
Ensure you have the Python `evdev` module provided by your OS package manager.
```bash
sudo apt update
sudo apt install python3-evdev
```

**2. Clone and Install**
Clone the repository and install the script as a standard system binary in `/usr/local/bin/`.
```bash
git clone [https://github.com/Husseinadq/linux-freetouch.git](https://github.com/Husseinadq/linux-freetouch.git)
cd linux-freetouch
sudo cp freetouch.py /usr/local/bin/linux-freetouch
sudo chmod +x /usr/local/bin/linux-freetouch
```

**3. Enable the Background Service**
Copy the provided systemd service file and enable it to start automatically on boot.
```bash
sudo cp freetouch.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now freetouch.service
```

---

## ⚙️ Configuration & Tuning

Every trackpad has a different glass texture, resolution, and sensitivity. You can easily tune how the swipes feel by editing the constants at the top of the installed script.

```bash
sudo nano /usr/local/bin/linux-freetouch
```

Find these variables at the top of the file:
* `EDGE_WIDTH_PERCENT = 0.05` — Defines how thick the "active zone" is on the edges. (Default: the outer 5% of the pad).
* `SWIPE_SENSITIVITY = 0.02` — Defines how far your finger has to travel to trigger 1 volume/brightness tick. (Decrease this number to make it more sensitive/faster).
* `PALM_THRESHOLD = 8` — The minimum touch size to be considered a palm. (Increase this if your actual fingers are being ignored; decrease it if your palm is accidentally triggering volume changes).

After saving your changes, restart the service to apply them:
```bash
sudo systemctl restart freetouch.service
```
### 🔄 How to Update
To update to the latest version, you do not need to uninstall the old one. Simply re-run the installation command to fetch the newest code and automatically restart the background service:

```bash
wget -qO- [https://raw.githubusercontent.com/Husseinadq/linux-freetouch/main/install.sh](https://raw.githubusercontent.com/Husseinadq/linux-freetouch/main/install.sh) | sudo bash
---

## 🛠️ Troubleshooting

**"The service is running, but swiping doesn't do anything."**
Ensure your Linux user is part of the `input` group, and that the `uinput` kernel module is loaded so the script can inject virtual keypresses.
```bash
sudo modprobe uinput
```

**"It says 'Could not find a compatible touchpad'."**
Run `sudo evtest` in your terminal to see a list of your hardware. If your trackpad has a highly unusual name that doesn't include "touchpad", "synaptics", "elan", or "gxtp", you may need to add your trackpad's specific keyword to the `keywords` array inside the `get_touchpad()` function.

---

## 🤝 Contributing
Pull requests are welcome! If you find a trackpad model that isn't recognized, or if you figure out how to map knuckle-knocks to screenshots via `ABS_MT_PRESSURE`, please open an issue or submit a PR.

## 📄 License
This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.


---

## 🗑️ Uninstallation

If you want to remove Linux Free Touch from your system, simply run these commands to stop the daemon and remove the files:

```bash
sudo systemctl disable --now freetouch.service
sudo rm /etc/systemd/system/freetouch.service
sudo systemctl daemon-reload
sudo rm /usr/local/bin/linux-freetouch
```

---

*Built with ❤️ by [Husseinadq](https://github.com/Husseinadq) for the Linux community.*