# Proton-Mail-Tray

Proton-Mail-Tray is a lightweight Linux application that provides a tray icon for quick access to Proton Mail (https://proton.me/mail). Currently, Proton Mail does not have a native tray icon feature, although it is on their roadmap for future updates. This application allows you to open and close Proton Mail from a tray icon.

## Table of Contents

- [Proton-Mail-Tray](#proton-mail-tray)
  - [Table of Contents](#table-of-contents)
  - [Why?](#why)
  - [Features](#features)
  - [Security Considerations](#security-considerations)
  - [Requirements](#requirements)
  - [Installation](#installation)
    - [Executable](#executable)
    - [Source](#source)
  - [Contributing](#contributing)
  - [License](#license)

## Why?

I prefer having quick access to select applications via a tray icon. Therefore, I created Proton-Mail-Tray to fill this gap and decided to share it with others who may find it useful.

## Features

- Simple and lightweight.
- Quick access to Proton Mail via a tray icon.
- Left click to open/close Proton Mail.
- Right click to quit the application.

## Security Considerations

Proton-Mail-Tray sends a SIGTERM to the Proton Mail application when closing it. As far as I'm aware, this should be completely harmless. If you have any reservations, you can build the executable yourself using the provided `scripts/build.sh`. All code is provided for full transparency.

## Requirements

The application has been tested on Linux Mint 21.3 Xfce 64-bit with Python 3.12. It should work on most Ubuntu/Debian-based Linux distributions and Python versions compatible with the packages listed in `requirements.txt`.

## Installation

### Executable

1. Download the `ProtonMailTray-vX.X.X` executable under releases to your desired location.
2. From the cli run `./ProtonMailTray-vX.X.X --proton-mail-path "/path/to/Proton Mail"`. This will set the path for the executable.
3. Run the executable.
4. (Optional) Add the executable to your startup programs for ease of use.

### Source

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/Proton-Mail-Tray.git
   ```
2. Navigate to the project directory:
   ```sh
   cd Proton-Mail-Tray
   ```
3. Create and activate a virtual environment (recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate 
   ```
4. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```
5. Run the application:
   ```sh
   python -m proton_mail_tray.app
   ```
6. Configure the path to the Proton Mail application if required:
   ```json
   {
    "proton_mail_path": "/path/to/Proton Mail Beta executable"
   }

## Contributing

Contributions are welcome. Please fork the repository and create a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.