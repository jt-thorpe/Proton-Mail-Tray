import json
import logging
import os
import sys
from typing import Optional

from proton_mail_tray.utils import find_proton_mail_path

logger = logging.getLogger(__name__)


def get_base_path() -> str:
    """Determine the base path of the application.

    Finds the base path of the application, whether it is ran via executable or source code.

    Returns:
        str: The base path of the application
    """
    if getattr(sys, 'frozen', False):  # if executable
        return sys._MEIPASS
    else:  # if source
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        sys.path.append(base_path)
        return base_path


def load_config(file_path: str) -> dict:
    """Load the configuration from a file.

    Args:
        file_path (str): The path to the configuration file.

    Returns:
        dict: The configuration, or empty if the file does not exist or is not valid JSON.
    """
    logger.info(f"Loading configuration from {file_path}")
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.warning(f"Unable to load configuration from {file_path}")
    return {}


def save_config(file_path: str, config: dict) -> None:
    """Save the configuration to a file.

    Args:
        file_path (str): The path to the configuration file.
        config (dict): The configuration to save.
    """
    logger.info(f"Saving configuration to {file_path}")
    try:
        with open(file_path, 'w') as f:
            json.dump(config, f)
            logger.info(f"Configuration saved to {file_path}")
    except Exception as e:
        logger.error(f"Unable to save configuration to {file_path}: {e}")


def get_proton_mail_path(args, file_path: str) -> Optional[str]:
    """Get the path to Proton Mail Beta, either from CLI, config, or find it.

    Args passed via CLI take precedence over the config file. If the path is not found in the config file, it will be
    searched for.

    Args:
        args (argparse.Namespace): The command-line arguments.
        file (str): The path to the configuration file.

    Returns:
        str or None: The path to Proton Mail Beta, or None if it could not be found.
    """
    config = load_config(file_path)
    if args.proton_mail_path is not None:
        logger.info(f"Proton Mail path provided via CLI: {args.proton_mail_path}")
        proton_mail_path = args.proton_mail_path
        config['proton_mail_path'] = proton_mail_path
        save_config(file_path, config)
    elif 'proton_mail_path' in config:
        # TODO: Improve this
        logger.info(f"Proton Mail path found in config: {config['proton_mail_path']}")
        proton_mail_path = config['proton_mail_path']
    else:
        logger.info("Proton Mail path not found in config, searching for it...")
        proton_mail_path = find_proton_mail_path()
        if proton_mail_path:
            config['proton_mail_path'] = proton_mail_path
            save_config(file_path, config)

    return proton_mail_path
