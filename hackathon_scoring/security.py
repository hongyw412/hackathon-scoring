"""인증 코드 해시 및 안전한 문자열 비교 기능."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 600_000
SALT_BYTES = 16


def hash_access_code(access_code: str) -> str:
    """인증 코드를 PBKDF2-HMAC-SHA256 해시 문자열로 변환합니다."""
    normalized = access_code.strip()
    if len(normalized) < 4:
        raise ValueError("인증 코드는 4자 이상이어야 합니다.")

    salt = secrets.token_bytes(SALT_BYTES)
    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        normalized.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    salt_text = base64.urlsafe_b64encode(salt).decode("ascii")
    key_text = base64.urlsafe_b64encode(derived_key).decode("ascii")

    return (
        f"{ALGORITHM}${PBKDF2_ITERATIONS}"
        f"${salt_text}${key_text}"
    )


def verify_access_code(access_code: str, stored_hash: str) -> bool:
    """입력 인증 코드와 저장된 PBKDF2 해시를 비교합니다."""
    if not access_code or not stored_hash:
        return False

    try:
        algorithm, iterations_text, salt_text, key_text = stored_hash.split(
            "$",
            maxsplit=3,
        )
        if algorithm != ALGORITHM:
            return False

        iterations = int(iterations_text)
        salt = base64.urlsafe_b64decode(salt_text.encode("ascii"))
        expected_key = base64.urlsafe_b64decode(key_text.encode("ascii"))

        actual_key = hashlib.pbkdf2_hmac(
            "sha256",
            access_code.strip().encode("utf-8"),
            salt,
            iterations,
        )
        return hmac.compare_digest(actual_key, expected_key)
    except (ValueError, TypeError, base64.binascii.Error):
        return False


def secure_compare(value: str, expected: str) -> bool:
    """관리자 비밀번호처럼 평문 환경변수 값을 안전하게 비교합니다."""
    return hmac.compare_digest(
        (value or "").encode("utf-8"),
        (expected or "").encode("utf-8"),
    )
