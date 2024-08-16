import argparse
import logging
import os
import subprocess
import sys
from logging.handlers import RotatingFileHandler

import psutil
from PySide6.QtCore import QObject, QThread
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from proton_mail_tray.config import get_base_path, get_proton_mail_path
from proton_mail_tray.utils import is_proton_mail_running, terminate_process

# Constants
BASE_PATH = get_base_path()
ICON_PATH = os.path.join(BASE_PATH, 'resources', 'icon', 'proton-mail.png')
LOG_DIR = os.path.join(BASE_PATH, 'logs')
CONFIG_FILE = os.path.join(BASE_PATH, 'config.json')
LOG_FILE = os.path.join(LOG_DIR, 'proton_mail_tray.log')


class ProtonMailTray(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        # Parser & args
        self.parser = self._setup_parser()
        self.args = self.parser.parse_args()

        # Logger
        self.logger = self._setup_logger(LOG_DIR, LOG_FILE)

        # Tray icon
        self.tray_icon = QSystemTrayIcon(QIcon(ICON_PATH), self)
        if self.tray_icon.icon().isNull():
            self.logger.warning(f"Unable to find Proton Mail Tray icon at: {ICON_PATH}")
        self.tray_icon.activated.connect(self._on_tray_icon_activated)

        # Menu
        menu = QMenu()
        quit_action = QAction("Quit")
        quit_action.triggered.connect(self.quit)
        menu.addAction(quit_action)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setVisible(True)
        self.tray_icon.show()

        # Setup monitor thread; watch for Proton Mail closure
        self.monitor_thread = QThread()
        self.monitor = SubprocessMonitor()
        self.monitor.moveToThread(self.monitor_thread)
        self.monitor_thread.started.connect(self.monitor.run)
        self.monitor_thread.start()

    def _setup_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description='Proton Mail Tray Application')
        parser.add_argument('--proton-mail-path', type=str, help='Manually specify the path to Proton Mail Beta')
        return parser

    def _setup_logger(self, log_dir: str, log_file: str) -> logging.Logger:
        """Setup logging configuration.

        Args:
            log_dir (str): The directory to store the log file.
            log_file (str): The path to the log file.

        Returns:
            logging.Logger: The logger instance.
        """
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
        logging.basicConfig(handlers=[handler], encoding='utf-8', level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        return logging.getLogger(__name__)

    def _on_tray_icon_activated(self) -> None:
        """Open or close Proton Mail when the tray icon is clicked.

        Args:
            reason (QSystemTrayIcon.ActivationReason): The reason the tray icon was activated.
        """
        self.logger.info("Tray icon activated with reason.")
        if is_proton_mail_running():
            self.logger.info("Closing Proton Mail")
            self._close_proton_mail()
        else:
            self.logger.info("Opening Proton Mail")
            self._open_proton_mail(get_proton_mail_path(self.args, CONFIG_FILE))

    def _open_proton_mail(self, proton_mail_path: str) -> None:
        """Open Proton Mail.

        Args:
            proton_mail_path (str): The path to the Proton Mail Beta executable.
        """
        try:
            process = subprocess.Popen([proton_mail_path])
            self.logger.info("Proton Mail opened successfully")
            self.monitor.set_proton_mail_subprocess(process)
        except Exception as e:
            self.logger.exception(f"Failed to open Proton Mail: {e}")

    def _close_proton_mail(self) -> None:
        """Close Proton Mail.

        If the process is not found or access is denied, log the exception.
        """
        proton_mail_pid = is_proton_mail_running()
        if proton_mail_pid:
            try:
                process = psutil.Process(proton_mail_pid)
                terminate_process(process)
                self.logger.info("Proton Mail closed successfully")
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                self.logger.exception(f"Failed to close Proton Mail: {e}")
        else:
            self.logger.info("Proton Mail is not running")


class SubprocessMonitor(QObject):
    def __init__(self):
        super().__init__()
        self._running = True  # Control flag for the worker loop
        self.proton_mail_subprocess = None
        self.logger = logging.getLogger(__name__)

    def set_proton_mail_subprocess(self, process: subprocess.Popen) -> None:
        """Set the Proton Mail subprocess to monitor.

        Args:
            process (subprocess.Popen): The Proton Mail subprocess to monitor.
        """
        self.proton_mail_subprocess = process
        self.logger.info(f"Subprocess Monitor: Proton Mail subprocess set: {process.pid}")

    def run(self):
        while self._running:
            if self.proton_mail_subprocess:
                if self.proton_mail_subprocess.poll() is None:
                    self.logger.info("Subprocess Monitor: Proton Mail is running")
                else:
                    self.logger.info("Subprocess Monitor: Proton Mail is not running")
                    self.proton_mail_subprocess.wait()
            else:
                self.logger.debug("Subprocess Monitor: No process to check.")
            QThread.sleep(3)

    def stop(self):
        self._running = False
        if self.proton_mail_subprocess and self.proton_mail_subprocess.poll() is None:
            self.logger.info("Subprocess Monitor: Closing Proton Mail")
            terminate_process(self.proton_mail_subprocess)


def main():
    app = ProtonMailTray(sys.argv)
    app.logger.info("Proton Mail Tray App started")

    # Begin app loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
