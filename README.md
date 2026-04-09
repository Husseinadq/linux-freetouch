# 🐧 Linux Free Touch

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Linux](https://img.shields.io/badge/Platform-Linux-blue.svg)]()
[![Python 3](https://img.shields.io/badge/Python-3.x-brightgreen.svg)]()
[![systemd](https://img.shields.io/badge/Init-systemd-lightgrey.svg)]()

**A universal, open-source user-space daemon that enables native edge-swipe gestures (Volume, Brightness, & Media) on Linux trackpads.**

Originally built to restore the **Huawei Free Touch** features on MateBook laptops running Ubuntu/Linux, this tool dynamically calibrates to work on almost any modern laptop trackpad that supports multi-touch hardware.

---

## 🎯 What It Does

```
 ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← TOP EDGE → → → → → → → → → → → → → → →
 ⏪ Swipe left: Seek Backward (←)                  Swipe right: Seek Forward (→) ⏩

 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │ ☀️                                                                          🔊 │
 │  B                                                                          V  │
 │  r                                                                          o  │
 │  i             ┌───────────────────────────────────────────┐                l  │
 │  g             │                                           │                u  │
 │  h             │           Normal Trackpad Area            │                m  │
 │  t             │         (untouched, works as usual)       │                e  │
 │  n             │                                           │                   │
 │  e             └───────────────────────────────────────────┘                U  │
 │  s                                                                          p  │
 │  s  ▲ Swipe up: Brighter                          Swipe up: Volume Up  ▲       │
 │     ▼ Swipe down: Dimmer                        Swipe down: Volume Down ▼      │
 └─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔍 The Problem It Solves

On Windows, laptops like the Huawei MateBook X Pro use a proprietary background service to detect when your finger slides along the extreme edges of the trackpad, allowing you to change volume and brightness. On Linux, standard drivers (`libinput` / `synaptics`) treat the entire pad as a standard mouse, meaning you lose these premium hardware features.

**Linux Free Touch** safely intercepts the raw hardware coordinate data via `evdev`, bypasses audio server permission issues by injecting virtual media keystrokes, and restores your hardware gestures natively.

---

## ✨ Features

| Gesture | Zone | Action |
|---------|------|--------|
| 🔊 Swipe Up / Down | Right edge | Volume Up / Down |
| ☀️ Swipe Up / Down | Left edge | Brightness Up / Down |
| ⏪ Swipe Left / Right | Top edge | Seek Backward / Forward in video timelines |
| ✋ Palm Rejection | Entire pad | Ignores large touches (palms) automatically |

**Plus:**
* 📐 **Dynamic Hardware Calibration** — Automatically reads your trackpad's physical X/Y axis dimensions to map the edge zones perfectly, regardless of make or model.
* 🪶 **Ultra-Lightweight** — Written in pure Python, running as an invisible `systemd` background service with virtually zero CPU overhead.
* 🔌 **Zero Config** — Works out of the box. No configuration files needed.

---

## 🖥️ Tested On

| Laptop | Trackpad | Status |
|--------|----------|--------|
| Huawei MateBook X Pro | ELAN | ✅ Fully working |

> **Your laptop not listed?** It should still work! The daemon auto-detects any trackpad that exposes multi-touch coordinates. If it works for you, please [open an issue](https://github.com/Husseinadq/linux-freetouch/issues) to add your laptop to this table.

---

## 🚀 Installation

### Method 1: Quick Install (Recommended)

Install the dependencies, download the daemon, and start the background service with a single command:

```bash
wget -qO- https://raw.githubusercontent.com/Husseinadq/linux-freetouch/main/install.sh | sudo bash
```

### Method 2: Manual Installation

If you prefer to audit the installation steps yourself:

**1. Install System Dependencies**
```bash
sudo apt update
sudo apt install python3-evdev
```

**2. Clone and Install**
```bash
git clone https://github.com/Husseinadq/linux-freetouch.git
cd linux-freetouch
sudo cp freetouch.py /usr/local/bin/linux-freetouch
sudo chmod +x /usr/local/bin/linux-freetouch
```

**3. Enable the Background Service**
```bash
sudo cp freetouch.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now freetouch.service
```

### ✅ Verify It's Working

After installation, check that the daemon is running:

```bash
sudo systemctl status freetouch.service
```

You should see **`active (running)`** in the output. Now try swiping the right edge of your trackpad — your volume should change!

---

## 🔄 How to Update

To update to the latest version, simply re-run the install command. It will overwrite the old binary and restart the service automatically:

```bash
wget -qO- https://raw.githubusercontent.com/Husseinadq/linux-freetouch/main/install.sh | sudo bash
```

---

## ⚙️ Configuration & Tuning

Every trackpad has a different glass texture, resolution, and sensitivity. You can tune how the swipes feel by editing the constants at the top of the installed script:

```bash
sudo nano /usr/local/bin/linux-freetouch
```

| Variable | Default | Description |
|----------|---------|-------------|
| `EDGE_WIDTH_PERCENT` | `0.05` | How thick the active zone is on the side edges (5% of pad width) |
| `TOP_EDGE_PERCENT` | `0.05` | How thick the active zone is on the top edge (5% of pad height) |
| `SWIPE_SENSITIVITY` | `0.02` | How far your finger must travel to trigger 1 tick. Decrease = faster response |
| `PALM_THRESHOLD` | `8` | Minimum touch size to be considered a palm. Increase if your fingers are being ignored |

After saving your changes, restart the service to apply them:
```bash
sudo systemctl restart freetouch.service
```

---

## 🛠️ Troubleshooting

<details>
<summary><strong>"The service is running, but swiping doesn't do anything."</strong></summary>

Ensure the `uinput` kernel module is loaded so the script can inject virtual keypresses:
```bash
sudo modprobe uinput
```

To make this persistent across reboots:
```bash
echo "uinput" | sudo tee /etc/modules-load.d/uinput.conf
```
</details>

<details>
<summary><strong>"It says 'Could not find a compatible touchpad'."</strong></summary>

Run `sudo evtest` in your terminal to see a list of your hardware devices. If your trackpad has an unusual name that doesn't include `touchpad`, `synaptics`, `elan`, `alps`, or `gxtp`, you'll need to add your trackpad's keyword to the `keywords` list inside the `get_touchpad()` function in the script.
</details>

<details>
<summary><strong>"How do I check the daemon logs?"</strong></summary>

View the live log output with:
```bash
sudo journalctl -u freetouch.service -f
```
</details>

---

## 🗑️ Uninstallation

To completely remove Linux Free Touch from your system:

```bash
sudo systemctl disable --now freetouch.service
sudo rm /etc/systemd/system/freetouch.service
sudo systemctl daemon-reload
sudo rm /usr/local/bin/linux-freetouch
```

---

## 🏗️ How It Works

```
┌──────────────┐     evdev      ┌──────────────────┐    uinput     ┌──────────┐
│   Trackpad   │ ──────────────▶│  Linux Free Touch │ ────────────▶│  System  │
│   Hardware   │  raw X/Y/touch │     (daemon)      │ virtual keys │  (DE/WM) │
└──────────────┘                └──────────────────┘               └──────────┘
```

1. **Reads** raw multi-touch coordinates from your trackpad via the Linux `evdev` interface
2. **Maps** the trackpad edges using the hardware-reported axis dimensions (no hardcoded values)
3. **Detects** directional swipes within the edge zones using coordinate deltas
4. **Injects** virtual keystrokes (`KEY_VOLUMEUP`, `KEY_BRIGHTNESSDOWN`, etc.) via `uinput`
5. Your desktop environment handles the keystrokes natively — no audio server or display manager integration needed

---

## 🤝 Contributing

Pull requests are welcome! Some ideas:

- 🧪 Test on your laptop and report compatibility
- 🖐️ Add new gesture zones (e.g., corner taps for Play/Pause or Mute)
- 🔧 Add support for non-Debian distros (Fedora, Arch)

Please [open an issue](https://github.com/Husseinadq/linux-freetouch/issues) or submit a PR.

## 📄 License

This project is licensed under the [MIT License](LICENSE) — see the LICENSE file for details.

---

*Built with ❤️ by [Husseinadq](https://github.com/Husseinadq) for the Linux community.*