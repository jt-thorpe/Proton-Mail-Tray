#!/bin/bash

### USAGE
# From Proton-Mail-Tray/ run `./scripts/build.sh` to build the executable

# Clean previous builds
rm -rf build dist

# Package with PyInstaller
pyinstaller --onefile \
            --windowed \
            --name "ProtonMailTray" \
            --add-data "resources/icon/proton-mail.png:resources/icon" \
            --add-data "logs:logs" \
            --add-data "configs/config.json:configs" \
            --add-data "configs/logging_config.json:configs" \
            --additional-hooks-dir "scripts/hook-proton_mail_tray.py" proton_mail_tray/app.py
