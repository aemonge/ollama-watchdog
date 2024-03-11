import unittest
from unittest.mock import patch

from src.libs.bash_run import bash_run


class TestBashRun(unittest.TestCase):
    @patch("src.libs.bash_run.subprocess.check_output")
    def test_bash_run_success(self, mock_check_output):
        # Mock the subprocess.check_output to return a fake command output
        mock_check_output.return_value = b"example.py\nexample.txt\n"

        # Define the content with the special run tag
        content = "Here is the output:\n <-- run: `ls` -->"
        expected_response = (
            "Here is the output:\n"
            " **ls**:\n"
            "\n"
            " ```bash\n"
            " example.py\n"
            " example.txt\n"
            " ```"  # Removed the extra space before the closing backticks
        )

        # Call the function and assert the expected response
        result = bash_run(content)
        self.assertEqual(result, expected_response)

        # Verify that subprocess.check_output was called with the correct command
        mock_check_output.assert_called_once_with(["ls"])

if __name__ == "__main__":
    unittest.main()
