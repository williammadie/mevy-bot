import unittest

from mevy_bot.authentication.authentication_handler import AuthenticationHandler


class TestAuthenticationHandler(unittest.TestCase):
    def test_hash_and_validate_password(self):
        password = "MySecurePassword123!"
        hashed_password = AuthenticationHandler.hash_password(password)

        # Ensure hashed password is different from plain password
        self.assertNotEqual(hashed_password, password.encode("utf8"))

        # Correct password should validate
        is_valid = AuthenticationHandler.is_password_correct(
            password, hashed_password)
        self.assertTrue(is_valid)

    def test_incorrect_password(self):
        correct_password = "CorrectPassword!"
        incorrect_password = "WrongPassword!"
        hashed_password = AuthenticationHandler.hash_password(correct_password)

        # Incorrect password should not validate
        is_valid = AuthenticationHandler.is_password_correct(
            incorrect_password, hashed_password)
        self.assertFalse(is_valid)

if __name__ == "__main__":
    unittest.main()
