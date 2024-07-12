import argparse
import logging
import os
import subprocess
import sys
from logging.handlers import RotatingFileHandler

import psutil
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from proton_mail_tray.config import get_proton_mail_path
from proton_mail_tray.utils import is_proton_mail_running, terminate_process


def setup_logger(log_dir: str, log_file: str) -> logging.Logger:
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
    logging.basicConfig(handlers=[handler], encoding='utf-8', level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)


def get_base_path() -> str:
    """Determine the base path of the application.

    Returns:
        str: The base path of the application
    """
    if getattr(sys, 'frozen', False):  # if executable
        return sys._MEIPASS
    else:  # if source
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.append(base_path)
        return base_path


def open_proton_mail(proton_mail_path: str) -> None:
    """Open Proton Mail.

    Args:
        proton_mail_path (str): The path to the Proton Mail Beta executable.
    """
    try:
        subprocess.Popen([proton_mail_path])
        logger.info("Proton Mail opened successfully")
    except Exception as e:
        logger.exception(f"Failed to open Proton Mail: {e}")


def close_proton_mail() -> None:
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


def on_tray_icon_activated(reason: QSystemTrayIcon.ActivationReason) -> None:
    """Open or close Proton Mail when the tray icon is clicked.

    Args:
        reason (QSystemTrayIcon.ActivationReason): The reason the tray icon was activated.
    """
    logger.info(f"Tray icon activated with reason: {reason}")
    if reason == QSystemTrayIcon.ActivationReason.Trigger:
        if is_proton_mail_running():
            logger.info("Closing Proton Mail")
            close_proton_mail()
        else:
            logger.info("Opening Proton Mail")
            open_proton_mail(get_proton_mail_path(args, CONFIG_FILE))


if __name__ == "__main__":
    # Argument parser setup
    parser = argparse.ArgumentParser(description='Proton Mail Tray Application')
    parser.add_argument('--proton-mail-path', type=str, help='Manually specify the path to Proton Mail Beta')
    args = parser.parse_args()

    # Paths to resources and logs
    BASE_PATH = get_base_path()
    ICON_PATH = os.path.join(BASE_PATH, 'resources', 'icon', 'proton-mail.png')
    LOG_DIR = os.path.join(BASE_PATH, 'logs')
    CONFIG_FILE = os.path.join(BASE_PATH, 'config.json')
    LOG_FILE = os.path.join(LOG_DIR, 'proton_mail_tray.log')

    # Setup logger
    logger = setup_logger(LOG_DIR, LOG_FILE)
    logger.info("======= Initializing Proton Mail Tray App =======")

    # Setup application and tray icon
    app = QApplication(sys.argv)
    tray_icon = QSystemTrayIcon(QIcon(ICON_PATH), parent=app)
    if tray_icon.icon().isNull():
        logger.warning(f"Unable to find Proton Mail Tray icon at: {ICON_PATH}")
    tray_icon.activated.connect(on_tray_icon_activated)

    # Setup tray icon menu
    menu = QMenu()
    quit_action = QAction("Quit")
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)
    tray_icon.setContextMenu(menu)
    tray_icon.setVisible(True)
    tray_icon.show()

    logger.info("Proton Mail Tray App started")
    sys.exit(app.exec())
