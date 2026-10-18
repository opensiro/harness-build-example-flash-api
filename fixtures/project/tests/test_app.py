import unittest
from app import normalize


class RepairTests(unittest.TestCase):
    def test_spaces(self):
        self.assertEqual(normalize("Hello World"), "hello_world")

    def test_already_normalized(self):
        self.assertEqual(normalize("simple"), "simple")


if __name__ == "__main__":
    unittest.main()
