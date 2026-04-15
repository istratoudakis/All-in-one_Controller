# All-in-One Productivity & AI Controller 🚀
### Developed for ΣΦΗΜΜΥ 17 / Pre-ΣΦΗΜΜΥ 10

A modular hardware-software ecosystem designed to streamline productivity by combining physical controls with a Python-based AI bridge. 

## 🛠 Project Overview
This project features an **ESP32-based controller** that interfaces with a Windows environment. It manages system functions (volume, app control) and integrates **Google Gemini AI** for voice-activated commands and intelligent task parsing.

## ✨ Key Features
- **Hardware Interface:** 13 mechanical buttons & a high-precision rotary encoder.
- **Custom GUI:** A 3.5" TFT (ILI9488) display running optimized C++ firmware.
- **Python Broker:** A robust serial bridge that handles system calls, Spotify API, and Discord integration.
- **AI Integration:** Voice-to-Command processing via Google Gemini AI.
- **Audio Processing:** Real-time noise calibration for high-accuracy voice recognition.

## 📂 Repository Structure
- `/Firmware`: ESP32 C++ source code (Arduino/PlatformIO).
- `/Python_Backend`: The "Broker" script, API handlers, and GUI.
- `/Hardware`: 3D models (.STL) and circuit diagrams.

## ⚙️ Installation & Setup

### 1. Hardware Setup
Flash the ESP32 with the code found in the `/Firmware` directory. Ensure you have the `TFT_eSPI` and `Adafruit_MCP23X17` libraries installed.

### 2. Python Backend
Install the necessary dependencies:
```bash
pip install -r requirements.txt
