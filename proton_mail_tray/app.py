import argparse
import json
import logging.config
import logging.handlers
import os
import pathlib
import subprocess
import sys

import psutil
from PySide6.QtCore import QThread
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from proton_mail_tray.config import get_base_path, get_proton_mail_path
from proton_mail_tray.monitor import SubprocessMonitor
from proton_mail_tray.utils import is_proton_mail_running, terminate_process

# Constants
BASE_PATH = get_base_path()
ICON_PATH = os.path.join(BASE_PATH, 'resources', 'icon', 'proton-mail.png')
LOG_DIR = os.path.join(BASE_PATH, 'logs')
CONFIG_FILE = os.path.join(BASE_PATH, 'configs/config.json')
LOG_FILE = os.path.join(LOG_DIR, 'proton_mail_tray.log')

# Logger
logger = logging.getLogger(__name__)


def setup_logger() -> None:
    config_file = pathlib.Path("configs/logging_config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)


def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Proton Mail Tray Application')
    parser.add_argument('--proton-mail-path', type=str, help='Manually specify the path to Proton Mail Beta')
    return parser


class ProtonMailTray(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        # Parser & args
        self.parser = setup_parser()
        self.args = self.parser.parse_args()

        # Tray icon
        self.tray_icon = QSystemTrayIcon(QIcon(ICON_PATH), self)
        if self.tray_icon.icon().isNull():
            logger.warning(f"Unable to find Proton Mail Tray icon at: {ICON_PATH}")
        self.tray_icon.activated.connect(self._on_tray_icon_activated)

        # Menu
        menu = QMenu()
        quit_action = QAction("Quit")
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setVisible(True)
        self.tray_icon.show()

        # Watch for external Proton Mail termination
        self.monitor_thread = QThread()
        self.monitor = SubprocessMonitor()
        self.monitor.moveToThread(self.monitor_thread)
        self.monitor_thread.started.connect(self.monitor.run)
        self.monitor_thread.start()

    def _on_tray_icon_activated(self) -> None:
        """Open or close Proton Mail when the tray icon is clicked.

        Args:
            reason (QSystemTrayIcon.ActivationReason): The reason the tray icon was activated.
        """
        if is_proton_mail_running():
            self._close_proton_mail()
        else:
            self._open_proton_mail(get_proton_mail_path(self.args, CONFIG_FILE))

    def _open_proton_mail(self, proton_mail_path: str) -> None:
        """Open Proton Mail.

        Args:
            proton_mail_path (str): The path to the Proton Mail Beta executable.
        """
        try:
            process = subprocess.Popen([proton_mail_path])
            logger.info("Proton Mail opened successfully")
            self.monitor.set_proton_mail_subprocess(process)
        except Exception as e:
            logger.exception(f"Failed to open Proton Mail: {e}")

    def _close_proton_mail(self) -> None:
        """Close Proton Mail.

        If the process is not found or access is denied, log the exception.
        """
        proton_mail_pid = is_proton_mail_running()
        if proton_mail_pid:
            try:
                process = psutil.Process(proton_mail_pid)
                terminate_process(process)
                logger.info("Proton Mail closed successfully")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.exception(f"Failed to close Proton Mail: {e}")
        else:
            logger.info("Proton Mail is not running")


def main():
    setup_logger()
    app = ProtonMailTray(sys.argv)
    logger.info("Proton Mail Tray App started")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
