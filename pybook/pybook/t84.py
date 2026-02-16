import base64
import hashlib


def short_url(url: str, l: int):
    digitsRequired = l * 3 // 4
    if l % 4 != 0:
        digitsRequired += 3

    raw = hashlib.sha256(url.encode("utf-8")).digest()
    if len(raw) < digitsRequired:
        raise ValueError("Not enough bytes")
    out = base64.urlsafe_b64encode(raw[:digitsRequired])[:l].decode("utf-8")
    return out
