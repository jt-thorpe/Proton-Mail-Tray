import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import psutil

base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(base_path)

from proton_mail_tray.utils import (find_proton_mail_path,
                                    is_proton_mail_running, terminate_process)


class TestFindProtonMailPath(unittest.TestCase):
    """Test the find_proton_mail_path function."""

    @patch('proton_mail_tray.utils.os.path.exists')
    def test_find_proton_mail_path_exists(self, mock_exists):
        """Test when Proton Mail is found at one of the paths."""
        mock_exists.side_effect = lambda path: path == "/usr/lib/proton-mail/Proton Mail Beta"

        result = find_proton_mail_path()
        self.assertEqual(result, "/usr/lib/proton-mail/Proton Mail Beta")

    @patch('proton_mail_tray.utils.os.path.exists')
    def test_find_proton_mail_path_not_exists(self, mock_exists):
        """Test when Proton Mail is not found at any of the paths."""
        mock_exists.return_value = False

        result = find_proton_mail_path()
        self.assertIsNone(result)


class TestIsProtonMailRunning(unittest.TestCase):
    """Test the is_proton_mail_running function."""

    @patch('proton_mail_tray.utils.psutil.process_iter')
    def test_proton_mail_running(self, mock_process_iter):
        """Test when Proton Mail is running."""
        mock_proc = MagicMock()
        mock_proc.info = {'name': 'Proton Mail Beta', 'pid': 1337}
        mock_process_iter.return_value = [mock_proc]

        pid = is_proton_mail_running()
        self.assertEqual(pid, 1337)

    @patch('proton_mail_tray.utils.psutil.process_iter')
    def test_proton_mail_not_running(self, mock_process_iter):
        """Test when Proton Mail is not running."""
        mock_process_iter.return_value = []

        pid = is_proton_mail_running()
        self.assertIsNone(pid)

    @patch('proton_mail_tray.utils.psutil.process_iter')
    def test_access_denied(self, mock_process_iter):
        """Test when AccessDenied is raised while checking the process."""
        mock_proc = MagicMock()
        mock_proc.info = {'name': 'SomeProcess', 'pid': 1337}
        mock_process_iter.return_value = [mock_proc]
        with patch('proton_mail_tray.utils.psutil.Process', side_effect=psutil.AccessDenied):
            pid = is_proton_mail_running()
            self.assertIsNone(pid)


class TestTerminateProcess(unittest.TestCase):
    """Test the terminate_process function."""
    # TODO: expand testing

    @patch('proton_mail_tray.utils.psutil')
    def test_normal_termination(self, mock_psutil):
        """Test when the process terminates normally."""
        mock_process = MagicMock()
        mock_process.children.return_value = []
        mock_psutil.TimeoutExpired = psutil.TimeoutExpired

        terminate_process(mock_process)

        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once_with(timeout=5)


    @patch('proton_mail_tray.utils.psutil')
    def test_process_timeout(self, mock_psutil):
        """Test when the process does not terminate in time."""
        mock_process = MagicMock()
        mock_process.children.return_value = []
        mock_process.wait.side_effect = psutil.TimeoutExpired(seconds=6)
        mock_psutil.TimeoutExpired = psutil.TimeoutExpired

        terminate_process(mock_process)

        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()  # kill in except


if __name__ == '__main__':
    unittest.main()