import unittest
import time
from app import app
from flask import session

class ComplexFlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

    def test_setname_empty(self):
        """Test error if username is empty"""
        response = self.client.post('/api/setname', json={"username": ""})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Nama tidak boleh kosong", response.data)

    def test_chat_without_name(self):
        """Chat without setting name (uses fallback 'Barts')"""
        response = self.client.post('/api/chat', json={"message": "Apa kabar?"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("Barts", data["reply"])  # Karena fallback ke nama default
        print("Fallback name test passed.")

    def test_chat_multiple_sessions(self):
        """Simulate multiple user sessions"""
        with self.client.session_transaction() as sess:
            sess["username"] = "UserA"
        response_a = self.client.post("/api/chat", json={"message": "Siapa kamu?"})
        self.assertEqual(response_a.status_code, 200)
        self.assertIn("UserA", response_a.get_json()["reply"])

        # Simulasi user lain
        other_client = app.test_client()
        with other_client.session_transaction() as sess:
            sess["username"] = "UserB"
        response_b = other_client.post("/api/chat", json={"message": "Siapa kamu?"})
        self.assertIn("UserB", response_b.get_json()["reply"])

    def test_response_contains_html_structure(self):
        """Ensure markdown is converted to HTML correctly"""
        with self.client.session_transaction() as sess:
            sess["username"] = "Tester"
        response = self.client.post('/api/chat', json={"message": "Buatkan saya tabel markdown"})
        data = response.get_json()
        self.assertIn("<table", data["reply_html"])
        self.assertIn("<tr", data["reply_html"])
        print("HTML rendering for table passed.")

    def test_chat_response_time(self):
        """Ensure GPT response is under 10 seconds"""
        with self.client.session_transaction() as sess:
            sess["username"] = "Ihsan"
        start = time.time()
        response = self.client.post('/api/chat', json={"message": "Apa itu Cipher?"})
        duration = time.time() - start
        self.assertLess(duration, 10)
        print(f"Chat response time test passed: {duration:.2f}s")

if __name__ == '__main__':
    unittest.main()
