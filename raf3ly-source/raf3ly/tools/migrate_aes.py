#!/usr/bin/env python3
"""Converts every S.d("base64+xor") literal (old scheme) into S.d(new int[]{...})
   AES-128-CTR ciphertext (new scheme). Safe to re-run: already-migrated literals are skipped."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
import base64, glob, json, os, re, sys
sys.path.insert(0, _HERE)
from aes import ctr

ROOT = _ROOT + "/app/src/java/com/raf3ly/app/"
K = json.load(open(_HERE + "/keys.json"))
OLD = bytes.fromhex(K["k1"])
KEY = bytes.fromhex(K["aeskey"])
PAT = re.compile(r'S\.d\("([^"]+)"\)')

def enc_blob(text):
    data = text.encode("utf-8")
    iv = os.urandom(16)
    blob = iv + ctr(KEY, iv, data)
    return "S.d(new int[]{%s})" % ",".join(str(b) for b in blob)

total = 0
for path in sorted(glob.glob(ROOT + "*.java")):
    if path.endswith("S.java"):
        continue
    s = open(path, encoding="utf-8").read()
    n = 0
    def rep(m):
        global n
        b64 = m.group(1)
        try:
            raw = base64.b64decode(b64)
        except Exception:
            return m.group(0)
        if len(raw) < 1:
            return m.group(0)
        plain = bytes(v ^ OLD[i % len(OLD)] for i, v in enumerate(raw)).decode("utf-8")
        n += 1
        return enc_blob(plain)
    s2 = PAT.sub(rep, s)
    if s2 != s:
        open(path, "w", encoding="utf-8").write(s2)
        print("migrated %d literals in %s" % (n, path.split("/")[-1]))
        total += n
print("total", total)
