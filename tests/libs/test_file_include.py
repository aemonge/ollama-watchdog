import unittest
from unittest.mock import mock_open, patch

from src.libs.file_include import replace_include_tags


class TestReplaceIncludeTags(unittest.TestCase):
    @patch("src.libs.file_include.os.path.expanduser")
    @patch(
        "src.libs.file_include.open",
        new_callable=mock_open,
        read_data="included content\n",
    )
    def test_replace_include_tag_success(self, mock_file, mock_expanduser):
        mock_expanduser.return_value = "file.txt"

        content = "Some content\n <-- include: file://file.txt -->"
        expected_result = (
            "Some content\n" " **file.txt**:\n\n" " ```\n" " included content\n" " ```"
        )

        result = replace_include_tags(content)
        self.assertEqual(result, expected_result)
        mock_file.assert_called_once_with("file.txt", "r")
        mock_expanduser.assert_called_once_with("file.txt")

    @patch("src.libs.file_include.os.path.expanduser")
    @patch("src.libs.file_include.open", side_effect=FileNotFoundError)
    def test_replace_include_tag_file_not_found(self, mock_file, mock_expanduser):
        mock_expanduser.return_value = "nonexistent.txt"

        content = "Some content\n <-- include: file://nonexistent.txt -->"
        expected_result = (
            "Some content\n"
            " **nonexistent.txt**:\n\n"
            " ```\n"
            "<-- include file not found -->\n"
            " ```"
        )

        result = replace_include_tags(content)
        self.assertEqual(result, expected_result)
        mock_file.assert_called_once_with("nonexistent.txt", "r")
        mock_expanduser.assert_called_once_with("nonexistent.txt")


if __name__ == "__main__":
    unittest.main()
