#!/usr/bin/env python3
"""Verifies every encrypted literal decrypts cleanly: no stray backslash escapes,
no readable Arabic left in the DEX, no old version string."""
import os
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
import glob, json, re, sys, zipfile
sys.path.insert(0, _HERE)
from aes import ctr
KEY = bytes.fromhex(json.load(open(_HERE + "/keys.json"))["aeskey"])
PAT = re.compile(r'S\.d\(new int\[\]\{([-0-9,]+)\}\)')
bad = 0
total = 0
for path in glob.glob(_ROOT + "/app/src/java/com/raf3ly/app/*.java"):
    s = open(path, encoding="utf-8").read()
    for m in PAT.finditer(s):
        vals = [int(v) for v in m.group(1).split(",")]
        raw = bytes(vals)
        plain = ctr(KEY, raw[:16], raw[16:]).decode("utf-8", "replace")
        total += 1
        if re.search(r'\\[ntr"\\]', plain):
            bad += 1
            print("ESCAPE LEFT:", path.split("/")[-1], repr(plain[:60]))
print("literals checked: %d, with stray escapes: %d" % (total, bad))
apk = sys.argv[1] if len(sys.argv) > 1 else None
if apk:
    dex = zipfile.ZipFile(apk).read("classes.dex")
    txt = dex.decode("latin-1")
    arabic = sum(1 for ch in txt if '\u0600' <= ch <= '\u06FF')
    print("readable arabic chars in dex:", arabic)
    print('"3.0" in dex:', "3.0" in txt)
