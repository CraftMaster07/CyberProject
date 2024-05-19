import unittest
from utils import sanitizeMessage

class TestSanitizeMessage(unittest.TestCase):
    def test_sanitize_message_no_xss(self):
        # Test with a message containing no XSS payloads
        msg = b"GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n"
        sanitized_msg = sanitizeMessage(msg)
        self.assertEqual(msg, sanitized_msg)

    def test_sanitize_message_with_xss(self):
        # Test with a message containing XSS payload
        msg = b"GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n<script>alert('XSS');</script>"
        print(msg.decode())
        sanitized_msg = sanitizeMessage(msg)
        print(sanitized_msg.decode())
        self.assertNotIn(b"<script>", sanitized_msg)

if __name__ == '__main__':
    unittest.main()
