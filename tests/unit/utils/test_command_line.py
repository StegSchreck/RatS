from unittest import TestCase
from unittest.mock import patch

from RatS.utils.command_line import print_progress_bar


class CommandLineUtilTest(TestCase):
    @staticmethod
    @patch('RatS.utils.command_line.get_command_line_dimensions')
    def test_progress_output(os_mock):
        os_mock.return_value = (50, 50)
        print_progress_bar(1, 100)
