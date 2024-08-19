import logging
import subprocess

from PySide6.QtCore import QObject, QThread

logger = logging.getLogger(__name__)


class SubprocessMonitor(QObject):
    """Monitor a subprocess and report its status."""

    def __init__(self):
        super().__init__()
        self._running = True  # remove?
        self.proton_mail_subprocess = None

    def set_proton_mail_subprocess(self, process: subprocess.Popen) -> None:
        """Set the Proton Mail subprocess to monitor.

        Args:
            process (subprocess.Popen): The Proton Mail subprocess to monitor.
        """
        self.proton_mail_subprocess = process
        logger.info(f"Proton Mail subprocess set: {process.pid}")

    def run(self):
        """Monitor the Proton Mail subprocess until it exits."""
        while self._running:
            if self.proton_mail_subprocess:
                if self.proton_mail_subprocess.poll() is not None:
                    self.proton_mail_subprocess.wait()
            QThread.sleep(1)
