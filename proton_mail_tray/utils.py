import logging
import os
from typing import Optional

import psutil
from psutil import AccessDenied, NoSuchProcess, TimeoutExpired

logger = logging.getLogger(__name__)


def find_proton_mail_path() -> Optional[str]:
    """Find the path to Proton Mail Beta.

    Returns:
        str or None: The path to Proton Mail Beta, or None if it could not be found.
    """
    possible_paths = [
        "/usr/lib/proton-mail/Proton Mail Beta",
        "/opt/proton-mail/Proton Mail Beta",
    ]

    logger.info("Searching for Proton Mail Beta...")
    for path in possible_paths:
        logger.info(f"Checking path: {path}")
        if os.path.exists(path):
            logger.info(f"Found Proton Mail Beta at: {path}")
            return path

    logger.info("Proton Mail Beta not found in standard locations.")
    return None


def is_proton_mail_running() -> Optional[int]:
    """Check if Proton Mail is running and return its PID.

    Returns:
        int or None: The PID of Proton Mail, or None if it is not running.
    """
    logger.info("Checking if Proton Mail is running")
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            process_name = proc.info['name']
            pid = proc.info['pid']
            if process_name.startswith('Proton Mail Bet'):  # Truncated name due to 15-character limit
                logger.info(f"Process name: {process_name}, process pid: {pid}")
                logger.info(f"Proton Mail is running with PID: {pid}")
                return pid
    except psutil.NoSuchProcess:
        logger.warning(f"Process {proc.info['name']} does not exist")
    except psutil.AccessDenied as e:
        logger.warning(f"Access denied while checking process {proc.info['name']}: {e}")
    logger.info("Proton Mail is not running")
    return None


def terminate_process(process: psutil.Process) -> None:
    """Terminate the given process and its children.

    Args:
        process (psutil.Process): The process to terminate.
    """
    try:
        logger.info(f"Terminating process {process.pid}")
        process.terminate()
        process.wait(timeout=5)  # Wait for the process to terminate
    except NoSuchProcess:
        logger.warning(f"Process {process.pid} does not exist")
    except AccessDenied:
        logger.error(f"Access denied while terminating process {process.pid}")
    except TimeoutExpired:
        logger.error(f"Process {process.pid} did not terminate in time, force killing")
        process.kill()
    except Exception as e:
        logger.exception(f"Failed to terminate process {process.pid}: {e}")
