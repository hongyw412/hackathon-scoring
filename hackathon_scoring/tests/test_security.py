from security import hash_access_code, secure_compare, verify_access_code


def test_access_code_hash_and_verify():
    code = "TEAM-ABCD1234"
    hashed = hash_access_code(code)

    assert hashed != code
    assert verify_access_code(code, hashed)
    assert not verify_access_code("wrong-code", hashed)


def test_secure_compare():
    assert secure_compare("admin-secret", "admin-secret")
    assert not secure_compare("admin-secret", "different")
