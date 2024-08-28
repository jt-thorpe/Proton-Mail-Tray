import argparse
import json
import logging.config
import logging.handlers
import subprocess
import sys
from pathlib import Path

import psutil
from PySide6.QtCore import QThread
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from proton_mail_tray.config import get_base_path, get_proton_mail_path
from proton_mail_tray.monitor import SubprocessMonitor
from proton_mail_tray.utils import is_proton_mail_running, terminate_process

# Logger
logger = logging.getLogger(__name__)


def setup_logger(logging_config_path: str) -> None:
    """Setup the logger using the logging configuration file.

    Args:
        logging_config_path (str): The path to the logging configuration file.
    """
    with open(logging_config_path) as f_in:
        config = json.load(f_in)
        config['handlers']['file']['filename'] = str(Path(sys._MEIPASS + config['handlers']['file']['filename']))
    logging.config.dictConfig(config)


def setup_parser() -> argparse.ArgumentParser:
    """Setup the command line parser.

    Returns:
        argparse.ArgumentParser: The command line parser.
    """
    parser = argparse.ArgumentParser(description='Proton Mail Tray Application')
    parser.add_argument('--proton-mail-path', type=str, help='Manually specify the path to Proton Mail Beta')
    return parser


class ProtonMailTray(QApplication):
    """Proton Mail Tray Application.

    Args:
        sys_argv (list): The system arguments.
        path_dict (dict): A dictionary containing the paths used by the application.
    """

    def __init__(self, sys_argv, path_dict: dict):
        super().__init__(sys_argv)

        # Paths
        self.path_dict = path_dict

        # Tray icon
        self.tray_icon = QSystemTrayIcon(QIcon(self.path_dict['icon_path']))
        if self.tray_icon.icon().isNull():
            logger.warning(f"Unable to find Proton Mail Tray icon at: {self.path_dict['icon_path']}")
        self.tray_icon.activated.connect(self._on_tray_icon_activated)

        # Menu
        self.menu = QMenu()
        self.quit_action = QAction("Quit")
        self.quit_action.triggered.connect(self._on_quit)
        self.menu.addAction(self.quit_action)
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.setVisible(True)
        self.tray_icon.show()

        # Watch for external Proton Mail termination
        self.monitor_thread = QThread()
        self.monitor = SubprocessMonitor()
        self.monitor.moveToThread(self.monitor_thread)
        self.monitor_thread.started.connect(self.monitor.start)
        self.monitor_thread.start()

    def _on_tray_icon_activated(self) -> None:
        """Open or close Proton Mail when the tray icon is clicked.

        Args:
            reason (QSystemTrayIcon.ActivationReason): The reason the tray icon was activated.
        """
        if is_proton_mail_running():
            self._close_proton_mail()
        else:
            self._open_proton_mail(self.path_dict['proton_mail_path'])

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

    def _on_quit(self):
        """Stop the monitor thread and close the application."""
        try:
            self.monitor.stop()
            self.monitor_thread.exit()
            self.monitor_thread.wait()
        except Exception as e:
            logger.exception(f"Failed to stop monitor thread: {e}")
            logger.info("Quitting")
        self.quit()


def main():
    # Parser & args
    parser = setup_parser()
    args = parser.parse_args()

    # Paths
    base_path = get_base_path()
    paths = {
        'base_path': str(base_path),
        'icon_path': str(base_path / 'resources' / 'icon' / 'proton-mail.png'),
        'config_path': str(base_path / 'configs' / 'config.json'),
        'logging_config_path': str(base_path / 'configs' / 'logging_config.json'),
        'proton_mail_path': get_proton_mail_path(args, str(base_path / 'configs' / 'config.json'))
    }

    # Logger
    print(paths['base_path'])
    setup_logger(paths['logging_config_path'])

    # Application
    app = ProtonMailTray(sys.argv, path_dict=paths)
    logger.info("========== Proton Mail Tray instance started ==========")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
