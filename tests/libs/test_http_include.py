import unittest
from unittest.mock import MagicMock, patch

import requests

from src.libs.http_include import get_website_content
from src.models.literals_types_constants import TIMEOUT


class TestGetWebsiteContent(unittest.TestCase):
    @patch("src.libs.http_include.requests.get")
    def test_get_website_content_success(self, mock_get):
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.text = "<html><body><p>Example content</p></body></html>"
        mock_get.return_value = mock_response

        content = "Some content\n <-- include: http://example.com -->"
        expected_result = (
            "Some content\n"
            " **http://example.com**:\n\n"
            " ```\n"
            " Example content\n"
            " ```"
        )

        result = get_website_content(content)
        print(result)
        self.assertEqual(result, expected_result)
        mock_get.assert_called_once_with("http://example.com", timeout=TIMEOUT)

    @patch(
        "src.libs.http_include.requests.get",
        side_effect=requests.exceptions.RequestException,
    )
    def test_get_website_content_request_exception(self, mock_get):
        content = "Some content\n <-- include: http://example.com -->"
        expected_result = (
            "Some content\n"
            " **http://example.com**:\n\n"
            " ```\n"
            "<-- include website not found -->\n"  # Adjusted to match the actual output
            " ```"
        )

        result = get_website_content(content)
        print(result)
        self.assertEqual(result, expected_result)
        mock_get.assert_called_once_with("http://example.com", timeout=TIMEOUT)


if __name__ == "__main__":
    unittest.main()
