# Fan Control Center

A simple fan control application designed specifically for Dell/Alienware computers. This tool allows you to easily manage your CPU and GPU fans without changing power profiles, CPU voltages, overclock settings etc., create custom profiles, and monitor temperature values.

![image](https://github.com/user-attachments/assets/e2c22346-299f-4253-904d-6bcc0414a9e1)


## Features

- 🌡️ Real-time CPU and GPU temperature monitoring
- 💨 Fan speed control (RPM and percentage based)
- 🎯 Pre-defined profiles:
  - Silent
  - Balanced
  - Performance
  - G Mode
  - Custom
- ⌨️ Customizable keyboard shortcuts for profiles
- 🌍 Multi-language support:
  - English
  - Turkish
  - Spanish
  - French
  - Portuguese
  - Arabic
  - Chinese
  - Russian
- 🚀 Automatic startup with Windows
- 🔄 Customizable monitoring interval
- 💻 System tray support

![image](https://github.com/user-attachments/assets/4a2a9650-5df3-422b-b28e-e4c8622b8520)

![image](https://github.com/user-attachments/assets/613ceca4-3018-4e06-868e-a07328d528c7)


## Supported Devices
- Dell G15 5530
- other models might work but I am working on them please let me now if it works or not with yours
  
## Requirements

- Windows 11 operating system
- Dell/Alienware computer
- Administrator rights
- Python 3.x (for running from source)

## Installation

1. Download the latest release from [Releases](https://github.com/mre31/fan-control-center/releases)
3. Run the downloaded .exe file
4. Accept administrator permissions

## Running from Source

Clone the repository
```
git clone https://github.com/mre31/fan-control-center.git
```
Navigate to project directory
```
cd fan-control-center
```
Install required packages
```
pip install -r requirements.txt
```
Run the application with admin privileges
```
python main.py
```
To build the app
```
.\build.ps1
```

## Usage

1. Launch the application
2. Select desired fan profile or create a custom one
3. Use sliders for manual fan speed adjustment
4. Assign keyboard shortcuts to profiles
5. Optionally keep the application running in system tray

> Sometimes if custom speeds are too low System takes control of the fans until it cools down to normal temps. Be aware.

## Contributing

1. Fork this repository
2. Create a new branch (`git checkout -b new-feature`)
3. Commit your changes (`git commit -am 'Added new feature'`)
4. Push to the branch (`git push origin new-feature`)
5. Create a Pull Request

# Disclaimer - Important Notice

This software ("Fan Control Center") is a third-party application developed for fan control of Dell Alienware computers.

## 1. Use at Your Own Risk
- The use of this software is entirely at your own risk.
- Manual control of fan speeds may cause your hardware to heat up.
- Improper fan settings may affect system performance and hardware lifespan.

## 2. Warranty Disclaimer
- This software is provided "AS IS".
- No warranties are given regarding the operation of the software or its fitness for any particular purpose.
- The developers cannot be held liable for any hardware damage, data loss, or other damages resulting from the use of this software.

## 3. Compatibility
- This software has only been tested on Dell Alienware systems.
- Operation on other systems is not guaranteed.
- Alienware Command Center (AWCC) software must be installed at least once.

## 4. Administrator Privileges
- The software requires administrator privileges for fan control.
- The software will not function properly without these permissions.

## 5. Third-Party Software
- This application is not affiliated with or endorsed by Dell Inc.
- This is an independent tool created for Dell/Alienware users.

---

*By using this software, you acknowledge and accept all the terms stated above.*

## License

This project is licensed under the BSD 3-Clause License.
