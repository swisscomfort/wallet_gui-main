"""Utility helpers for wallet-related pattern scoring."""

from __future__ import annotations

import hashlib
import re

B58_ALPH = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58decode_check(text: str) -> bytes:
    """Decode Base58Check data and validate the checksum."""
    num = 0
    for char in text:
        if char not in B58_ALPH:
            raise ValueError("bad base58")
        num = num * 58 + B58_ALPH.index(char)
    full = num.to_bytes((num.bit_length() + 7) // 8, "big")
    if len(full) < 4:
        raise ValueError("too short")
    data, checksum = full[:-4], full[-4:]
    if hashlib.sha256(hashlib.sha256(data).digest()).digest()[:4] != checksum:
        raise ValueError("bad checksum")
    return data


def is_valid_wif(candidate: str) -> bool:
    try:
        data = b58decode_check(candidate)
    except Exception:
        return False
    return data[:1] in (b"\x80", b"\xef") and len(data) in (33, 34)


def bech32_polymod(values: list[int]) -> int:
    generators = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for value in values:
        top = (chk >> 25) & 0xFF
        chk = ((chk & 0x1FFFFFF) << 5) ^ value
        for i, generator in enumerate(generators):
            if (top >> i) & 1:
                chk ^= generator
    return chk


def bech32_hrp_expand(hrp: str) -> list[int]:
    return [ord(char) >> 5 for char in hrp] + [0] + [ord(char) & 31 for char in hrp]


def bech32_verify(addr: str, hrps: tuple[str, ...] = ("bc", "tb")) -> bool:
    addr = addr.strip().lower()
    if any(c < 33 or c > 126 for c in map(ord, addr)):
        return False
    pos = addr.rfind("1")
    if pos == -1:
        return False
    hrp, data = addr[:pos], addr[pos + 1 :]
    if hrp not in hrps:
        return False
    charset = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"
    try:
        values = [charset.index(c) for c in data]
    except ValueError:
        return False
    return bech32_polymod(bech32_hrp_expand(hrp) + values) == 1


LEGACY_ADDR = re.compile(r"(?:^|[^A-Za-z0-9])([13][1-9A-HJ-NP-Za-km-z]{25,34})(?:[^A-Za-z0-9]|$)")
BECH32_ADDR = re.compile(r"(bc1[ac-hj-np-z02-9]{25,87}|tb1[ac-hj-np-z02-9]{25,87})")
WIF_RE = re.compile(r"(5[HJK][1-9A-HJ-NP-Za-km-z]{49,51}|[KL][1-9A-HJ-NP-Za-km-z]{51,52})")
ETH_PRIV_HEX = re.compile(r"\\b0x[a-fA-F0-9]{64}\\b")


def score_text(text: str) -> tuple[int, list[str]]:
    score = 0
    reasons: list[str] = []

    bech = BECH32_ADDR.findall(text)
    good_bech = [addr for addr in bech if bech32_verify(addr)]
    if good_bech:
        score += 4 * len(good_bech)
        reasons.append(f"{len(good_bech)} bech32")

    leg = [match.group(1) for match in LEGACY_ADDR.finditer(text)]
    good_leg = []
    for addr in leg:
        try:
            decoded = b58decode_check(addr)
            if decoded[:1] in (b"\x00", b"\x05", b"\x6f"):
                good_leg.append(addr)
        except Exception:
            continue
    if good_leg:
        score += 3 * len(good_leg)
        reasons.append(f"{len(good_leg)} legacy")

    wifs = WIF_RE.findall(text)
    good_wifs = [w for w in wifs if is_valid_wif(w)]
    if good_wifs:
        score += 15
        reasons.append("valid WIF")

    if ETH_PRIV_HEX.search(text):
        score += 10
        reasons.append("eth priv hex")

    return score, reasons

