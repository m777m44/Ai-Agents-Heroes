#!/usr/bin/env python3
"""Repairs Java escape sequences inside already-encrypted literals.

The first encryption pass took the *source text* of a literal, so `\\n` ended up as two
characters (backslash + n) instead of a newline. This decrypts every S.d blob, converts
the escapes, and re-encrypts. Idempotent.
"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
import glob, json, os, re, sys
sys.path.insert(0, _HERE)
from aes import ctr

ROOT = _ROOT + "/app/src/java/com/raf3ly/app/"
KEY = bytes.fromhex(json.load(open(_HERE + "/keys.json"))["aeskey"])
PAT = re.compile(r'S\.d\(new int\[\]\{([-0-9,]+)\}\)')
ESC = re.compile(r'\\([ntr"\\])')
MAP = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}

def blob(text):
    data = text.encode("utf-8")
    iv = os.urandom(16)
    return "S.d(new int[]{%s})" % ",".join(str(b) for b in iv + ctr(KEY, iv, data))

fixed = 0
for path in sorted(glob.glob(ROOT + "*.java")):
    if path.endswith("S.java"):
        continue
    s = open(path, encoding="utf-8").read()
    def rep(m):
        global fixed
        vals = [int(v) for v in m.group(1).split(",")]
        raw = bytes(vals)
        plain = ctr(KEY, raw[:16], raw[16:]).decode("utf-8", "replace")
        if not ESC.search(plain):
            return m.group(0)
        fixed += 1
        return blob(ESC.sub(lambda e: MAP[e.group(1)], plain))
    out = PAT.sub(rep, s)
    if out != s:
        open(path, "w", encoding="utf-8").write(out)
        print("fixed escapes in", path.split("/")[-1])
print("literals repaired:", fixed)
