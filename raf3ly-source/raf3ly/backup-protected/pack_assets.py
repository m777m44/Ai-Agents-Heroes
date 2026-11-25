#!/usr/bin/env python3
"""Encrypts app/src/assets/*.txt into build/assets/*.bin  ([16-byte IV][AES-128-CTR])."""
import hashlib, json, os, sys
sys.path.insert(0, "/home/user/raf3ly/tools")
from aes import ctr
ROOT = "/home/user/raf3ly"
KEY = bytes.fromhex(json.load(open(ROOT + "/tools/keys.json"))["aeskey"])
SRC, OUT = ROOT + "/app/src/assets", ROOT + "/build/assets"
os.makedirs(OUT, exist_ok=True)
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".txt"):
        continue
    data = open(os.path.join(SRC, f), "rb").read()
    iv = os.urandom(16)
    enc = iv + ctr(KEY, iv, data)
    name = {"i18n_en.txt": "d.bin"}.get(f, f[:-4] + ".bin")
    open(os.path.join(OUT, name), "wb").write(enc)
    print("packed %s -> %s (%d -> %d bytes, AES-128-CTR)" % (f, name, len(data), len(enc)))

# integrity asset: SHA-256 of the exact classes.dex that ships in the APK
dex = sys.argv[1] if len(sys.argv) > 1 else None
LIBS = sys.argv[2] if len(sys.argv) > 2 else None
if dex and os.path.exists(dex):
    blob = hashlib.sha256(open(dex, "rb").read()).digest()
    order = ["arm64-v8a", "armeabi-v7a", "x86_64", "x86"]
    for abi in order:
        p = os.path.join(LIBS, abi, "libnd.so") if LIBS else ""
        if p and os.path.exists(p):
            blob += hashlib.sha256(open(p, "rb").read()).digest()
        else:
            blob += b"\x00" * 32
    iv = os.urandom(16)
    open(os.path.join(OUT, "i.bin"), "wb").write(iv + ctr(KEY, iv, blob))
    print("packed integrity asset i.bin -> %d bytes (dex + %d native libs)" % (len(blob), len(blob) // 32 - 1))
