"""
GlycoTwin — Authentication & Database Tests
Tests password hashing, user creation, login, workspace isolation.
"""
import unittest
import sys
import os
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class TestPasswordSecurity(unittest.TestCase):

    def test_password_hash_not_plaintext(self):
        from app.auth import hash_password
        pw = "TestPassword1"
        hashed = hash_password(pw)
        self.assertNotEqual(pw, hashed)
        self.assertNotIn(pw, hashed)
        self.assertTrue(len(hashed) > 20)

    def test_password_verify_correct(self):
        from app.auth import hash_password, verify_password
        pw = "MySecurePass9"
        h = hash_password(pw)
        self.assertTrue(verify_password(pw, h))

    def test_password_verify_wrong(self):
        from app.auth import hash_password, verify_password
        pw = "MySecurePass9"
        h = hash_password(pw)
        self.assertFalse(verify_password("WrongPass9", h))

    def test_different_hashes_for_same_password(self):
        from app.auth import hash_password
        pw = "SamePassword1"
        h1 = hash_password(pw)
        h2 = hash_password(pw)
        # Argon2 salts are random → hashes differ
        self.assertNotEqual(h1, h2)

    def test_validate_email_valid(self):
        from app.auth import validate_email
        self.assertIsNone(validate_email("user@example.com"))

    def test_validate_email_invalid(self):
        from app.auth import validate_email
        self.assertIsNotNone(validate_email("not-an-email"))
        self.assertIsNotNone(validate_email("@no-user.com"))

    def test_validate_password_strength(self):
        from app.auth import validate_password
        self.assertIsNotNone(validate_password("short"))
        self.assertIsNotNone(validate_password("alllowercase1"))
        self.assertIsNotNone(validate_password("NoDigitHere"))
        self.assertIsNone(validate_password("ValidPass1"))

    def test_password_mismatch(self):
        from app.auth import validate_password
        err = validate_password("ValidPass1", "DifferentPass1")
        self.assertIsNotNone(err)
        self.assertIn("match", err.lower())


class TestDatabaseOperations(unittest.TestCase):

    def setUp(self):
        """Use a temp database for isolation."""
        import src.database.db as db_module
        self._original_db_path = db_module.DB_PATH
        self._temp_dir = tempfile.mkdtemp()
        db_module.DB_PATH = Path(self._temp_dir) / "test_glycotwin.db"
        db_module.init_db()

    def tearDown(self):
        import src.database.db as db_module
        db_module.DB_PATH = self._original_db_path
        # Clean up temp files
        import shutil
        shutil.rmtree(self._temp_dir, ignore_errors=True)

    def test_create_user(self):
        from src.database.db import create_user, get_user_by_email
        uid = create_user("Test User", "test@example.com", "fakehash", "researcher")
        self.assertIsNotNone(uid)
        self.assertGreater(uid, 0)
        user = get_user_by_email("test@example.com")
        self.assertIsNotNone(user)
        self.assertEqual(user["display_name"], "Test User")

    def test_duplicate_email_rejected(self):
        from src.database.db import create_user
        create_user("User One", "dup@example.com", "hash1")
        with self.assertRaises(Exception):
            create_user("User Two", "dup@example.com", "hash2")

    def test_password_hash_stored_not_plaintext(self):
        from src.database.db import create_user, get_user_by_email
        from app.auth import hash_password
        pw = "TestPw123"
        hashed = hash_password(pw)
        create_user("Secure", "secure@test.com", hashed)
        row = get_user_by_email("secure@test.com")
        stored_hash = row["password_hash"]
        self.assertNotEqual(stored_hash, pw)
        self.assertIn("$argon2", stored_hash)

    def test_workspace_user_isolation(self):
        from src.database.db import create_user, create_workspace, get_workspace
        from app.auth import hash_password
        uid1 = create_user("User 1", "u1@test.com", hash_password("Pass1abc"))
        uid2 = create_user("User 2", "u2@test.com", hash_password("Pass2abc"))
        wid = create_workspace(uid1, "User1 WS", participant_id="5")
        # User 2 should NOT be able to access user 1's workspace
        result = get_workspace(wid, uid2)
        self.assertIsNone(result)
        # User 1 CAN access their own workspace
        result = get_workspace(wid, uid1)
        self.assertIsNotNone(result)


class TestAuthFlow(unittest.TestCase):

    def setUp(self):
        import src.database.db as db_module
        from app.auth import register_user, authenticate_user
        self._original_db_path = db_module.DB_PATH
        self._temp_dir = tempfile.mkdtemp()
        db_module.DB_PATH = Path(self._temp_dir) / "test_auth.db"
        db_module.init_db()
        self.register_user = register_user
        self.authenticate_user = authenticate_user

    def tearDown(self):
        import src.database.db as db_module
        db_module.DB_PATH = self._original_db_path
        import shutil
        shutil.rmtree(self._temp_dir, ignore_errors=True)

    def test_valid_registration(self):
        ok, msg, uid = self.register_user("Alice", "alice@test.com", "ValidPass1", "ValidPass1")
        self.assertTrue(ok)
        self.assertIsNotNone(uid)

    def test_invalid_email_registration(self):
        ok, msg, uid = self.register_user("Bob", "not-an-email", "ValidPass1", "ValidPass1")
        self.assertFalse(ok)
        self.assertIsNone(uid)

    def test_password_mismatch_registration(self):
        ok, msg, uid = self.register_user("Carol", "carol@test.com", "ValidPass1", "DifferentPass2")
        self.assertFalse(ok)

    def test_duplicate_email_registration(self):
        self.register_user("Dave", "dave@test.com", "ValidPass1", "ValidPass1")
        ok, msg, uid = self.register_user("Dave2", "dave@test.com", "ValidPass1", "ValidPass1")
        self.assertFalse(ok)

    def test_valid_login(self):
        self.register_user("Eve", "eve@test.com", "ValidPass1", "ValidPass1")
        ok, msg, user = self.authenticate_user("eve@test.com", "ValidPass1")
        self.assertTrue(ok)
        self.assertIsNotNone(user)
        self.assertNotIn("password_hash", user)
        self.assertNotIn("password", user)

    def test_wrong_password_login(self):
        self.register_user("Frank", "frank@test.com", "ValidPass1", "ValidPass1")
        ok, msg, user = self.authenticate_user("frank@test.com", "WrongPass9")
        self.assertFalse(ok)
        self.assertIsNone(user)

    def test_nonexistent_user_login(self):
        ok, msg, user = self.authenticate_user("nobody@test.com", "AnyPass1")
        self.assertFalse(ok)
        self.assertIsNone(user)


if __name__ == "__main__":
    unittest.main()
