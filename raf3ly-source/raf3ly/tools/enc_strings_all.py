#!/usr/bin/env python3
"""Wraps every plain Arabic literal in the Java sources with S.d(new int[]{...})
(AES-128-CTR ciphertext, same scheme as tools/migrate_aes.py).

Idempotent: literals that are already inside S.d(...) are skipped, so it is safe to
run before every build (build.sh does) and newly written UI text is encrypted too.
"""
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
import glob, json, os, random, re, sys
sys.path.insert(0, _HERE)
from aes import ctr

ROOT = _ROOT + "/app/src/java/com/raf3ly/app/"
KEY = bytes.fromhex(json.load(open(_HERE + "/keys.json"))["aeskey"])
AR = re.compile(r'"((?:[^"\\]|\\.)*)"')

ESC = re.compile(r'\\([ntr"\\\\])')
MAP = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}


def unescape(lit):
    """Java source escapes -> the value the JVM would produce at runtime."""
    return ESC.sub(lambda m: MAP[m.group(1)], lit)


def blob(text):
    data = text.encode("utf-8")
    iv = os.urandom(16)
    enc = iv + ctr(KEY, iv, data)
    return "S.d(new int[]{%s})" % ",".join(str(b) for b in enc)

total = 0
for path in sorted(glob.glob(ROOT + "*.java")):
    if path.endswith(("S.java",)):
        continue
    s = open(path, encoding="utf-8").read()
    out, last, n = [], 0, 0
    for m in AR.finditer(s):
        lit = m.group(1)
        if not any('\u0600' <= ch <= '\u06FF' for ch in lit):
            continue
        if s[max(0, m.start() - 5):m.start()].endswith("S.d("):
            continue
        out.append(s[last:m.start()])
        out.append(blob(unescape(lit)))
        last = m.end()
        n += 1
    if n:
        out.append(s[last:])
        open(path, "w", encoding="utf-8").write("".join(out))
        print("encrypted %d strings in %s" % (n, path.split("/")[-1]))
        total += n
print("total", total)
