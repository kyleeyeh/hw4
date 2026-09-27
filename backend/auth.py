"""Password hashing + verification for Campus Customs.

Canonical scheme for every account we create:

    pbkdf2_sha256$<iterations>$<salt_hex>$<hash_hex>

- PBKDF2-HMAC-SHA256, 600,000 iterations (OWASP-recommended floor for 2023+).
- A fresh 16-byte random salt per user, so identical passwords hash differently
  and a stolen table can't be attacked with a single precomputed rainbow table.
- Only the salted hash is ever stored. The plaintext password is never written to
  disk, never logged, and never returned by any endpoint.

Verification is constant-time (hmac.compare_digest) to avoid timing side channels.

The seed DB shipped a different, undocumented 3-part variant
(`pbkdf2_sha256$salt$hash`, no iteration count). We cannot reproduce or verify those
hashes without the missing parameter, so `verify_password` treats any hash that is not
in our 4-part scheme as unverifiable. The documented test account is migrated to this
scheme on startup (see db.ensure_seed_logins).
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 600_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(stored: str, password: str) -> bool:
    """True iff `password` matches a hash we produced. Constant-time.

    Only our 4-part scheme is verifiable; anything else (e.g. the legacy seed hashes)
    returns False rather than raising.
    """
    try:
        algorithm, iterations_s, salt_hex, digest_hex = stored.split("$")
        if algorithm != ALGORITHM:
            return False
        iterations = int(iterations_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
    except (ValueError, AttributeError):
        return False
    calc = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(calc, expected)
