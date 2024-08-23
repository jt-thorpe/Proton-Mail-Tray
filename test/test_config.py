import argparse
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from proton_mail_tray.config import (get_base_path, get_proton_mail_path,
                                     load_config, save_config)


class TestGetBasePath(unittest.TestCase):
    """Test the get_base_path function."""

    def test_get_base_path(self):
        """Test getting the base path."""
        expected = Path.cwd()
        actual = get_base_path()

        self.assertEqual(expected, actual)


class TestSaveConfig(unittest.TestCase):
    """Test the save_config function."""

    def test_save_config(self):
        """Test saving a configuration."""
        file = "test/test_resources/test_config.json"
        config = {"key": "value"}

        save_config(file, config)

        with open(file, 'r') as f:
            expected = {"key": "value"}
            actual = json.load(f)

        self.assertEqual(expected, actual)

    def test_save_config_invalid_file(self):
        """Test saving a configuration to an invalid file."""
        file = "bad/path/to/test_config.json"
        config = {"key": "value"}

        save_config(file, config)

        expected = {}
        actual = load_config(file)

        self.assertEqual(expected, actual)


class TestLoadConfig(unittest.TestCase):
    """Test the load_config function."""

    def test_load_config(self):
        """Test loading a configuration."""
        file = "test/test_resources/test_config.json"
        with open(file, 'w') as f:
            json.dump({"key": "value"}, f)

        expected = {"key": "value"}
        actual = load_config(file)

        self.assertEqual(expected, actual)

    def test_load_config_no_file(self):
        """Test loading a configuration that does not exist."""
        file = "bad/path/to/test_config.json"
        expected = {}
        actual = load_config(file)

        self.assertEqual(expected, actual)

    def test_load_config_invalid_json(self):
        """Test loading a configuration that is not valid JSON."""
        file = "test/test_resources/test_config.json"
        with open(file, 'w') as f:
            f.write("invalid")

        expected = {}
        actual = load_config(file)

        self.assertEqual(expected, actual)


class TestGetProtonMailPath(unittest.TestCase):

    @patch('proton_mail_tray.config.load_config')
    @patch('proton_mail_tray.config.save_config')
    @patch('proton_mail_tray.config.find_proton_mail_path')
    def test_path_from_cli(self, mock_find, mock_save, mock_load):
        """Test getting the Proton Mail path from the CLI."""
        mock_load.return_value = {}
        args = argparse.Namespace(proton_mail_path='/path/from/cli')
        file_path = 'config_file_path'

        result = get_proton_mail_path(args, file_path)

        self.assertEqual(result, '/path/from/cli')
        mock_save.assert_called_once_with(file_path, {'proton_mail_path': '/path/from/cli'})
        mock_find.assert_not_called()

    @patch('proton_mail_tray.config.load_config')
    @patch('proton_mail_tray.config.save_config')
    @patch('proton_mail_tray.config.find_proton_mail_path')
    def test_path_from_config(self, mock_find, mock_save, mock_load):
        """Test getting the Proton Mail path from the configuration file."""
        mock_load.return_value = {'proton_mail_path': '/path/from/config'}
        args = argparse.Namespace(proton_mail_path=None)
        file_path = 'config_file_path'

        result = get_proton_mail_path(args, file_path)

        self.assertEqual(result, '/path/from/config')
        mock_save.assert_not_called()
        mock_find.assert_not_called()

    @patch('proton_mail_tray.config.load_config')
    @patch('proton_mail_tray.config.save_config')
    @patch('proton_mail_tray.config.find_proton_mail_path')
    def test_path_not_found_in_config_or_cli(self, mock_find, mock_save, mock_load):
        """Test finding the Proton Mail path."""
        mock_load.return_value = {}
        mock_find.return_value = '/path/found/automatically'
        args = argparse.Namespace(proton_mail_path=None)
        file_path = 'config_file_path'

        result = get_proton_mail_path(args, file_path)

        self.assertEqual(result, '/path/found/automatically')
        mock_save.assert_called_once_with(file_path, {'proton_mail_path': '/path/found/automatically'})

    @patch('proton_mail_tray.config.load_config')
    @patch('proton_mail_tray.config.save_config')
    @patch('proton_mail_tray.config.find_proton_mail_path')
    def test_path_not_found_at_all(self, mock_find, mock_save, mock_load):
        """Test when the Proton Mail path is not found at all."""
        mock_load.return_value = {}
        mock_find.return_value = None
        args = argparse.Namespace(proton_mail_path=None)
        file_path = 'config_file_path'

        result = get_proton_mail_path(args, file_path)

        self.assertIsNone(result)
        mock_save.assert_not_called()


if __name__ == '__main__':
    unittest.main()
