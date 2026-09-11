"""Regression: bcrypt hash/verify round-trip for auth compatibility."""
from app.core.security import get_password_hash, verify_password


def test_password_hash_verify_roundtrip():
    plain = "cropshield123"
    hashed = get_password_hash(plain)
    assert hashed.startswith("$2")
    assert verify_password(plain, hashed) is True
    assert verify_password("wrong-password", hashed) is False
    assert verify_password(plain, "") is False
    assert verify_password("", hashed) is False


def test_password_hash_is_not_plaintext():
    plain = "cropshield123"
    hashed = get_password_hash(plain)
    assert hashed != plain
    assert plain not in hashed
