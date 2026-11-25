#!/usr/bin/env python3
"""Regenerates the scrambled certificate fingerprint inside Guard.java.

Usage: gen_guard.py <path-to-cert-DER-or-hex>
The value fed here MUST be the SHA-256 of the certificate that signs the APK,
otherwise Guard kills the app on start (that is the anti-tamper contract).
"""
import re
import sys

K = 0x3F
GUARD = "/home/user/raf3ly/app/src/java/com/raf3ly/app/Guard.java"

def block(values):
    rows = []
    for i in range(0, len(values), 12):
        rows.append("            " + ", ".join("0x%04X" % v for v in values[i:i + 12]) + ",")
    return "\n".join(rows)

def main():
    digest = sys.argv[1].strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        sys.exit("expected 64 hex chars, got: " + digest)
    vals = [ord(c) ^ K for c in digest]
    src = open(GUARD, encoding="utf-8").read()
    new, n = re.subn(
        r"(private static final char\[\] E = \{\n).*?(\n    \};)",
        lambda m: m.group(1) + block(vals) + m.group(2),
        src,
        flags=re.S,
    )
    if n != 1:
        sys.exit("Guard.java: E array not found (%d matches)" % n)
    open(GUARD, "w", encoding="utf-8").write(new)
    print("Guard.E <= " + digest)

main()
