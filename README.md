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
    - [Building the executable yourself](#building-the-executable-yourself)
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

1. Download the `ProtonMailTray-vX.X.X` executable under releases to your desired location.
2. From the cli run `./ProtonMailTray-vX.X.X --proton-mail-path "/path/to/Proton Mail"`. This will set the path for the executable.
3. Run the executable with `./ProtonMailTray-vX.X.X`
4. (Optional) Add the executable to your startup programs for ease of use.

### Building the executable yourself

1. clone the repo.
2. navigate into the `Proton-Mail-Tray/` directory.
3. run `./scripts/build.sh`.
4. once complete, you can now run the executable as above.

## Contributing

Contributions are welcome. Please fork the repository and create a pull request with your changes. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
