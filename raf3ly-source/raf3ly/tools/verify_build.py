#!/usr/bin/env python3
"""Fails the build unless assets/i.bin matches the shipped code and native libraries."""
import hashlib, json, sys, zipfile
sys.path.insert(0, "/home/user/raf3ly/tools")
from aes import ctr
KEY = bytes.fromhex(json.load(open("/home/user/raf3ly/tools/keys.json"))["aeskey"])
apk = sys.argv[1]
with zipfile.ZipFile(apk) as z:
    dex = z.read("classes.dex")
    blob = ctr(KEY, z.read("assets/i.bin")[:16], z.read("assets/i.bin")[16:])
want_dex = blob[:32]
got_dex = hashlib.sha256(dex).digest()
if want_dex != got_dex:
    sys.exit("BUILD FAILED: dex digest mismatch (%s vs %s)" % (want_dex.hex()[:16], got_dex.hex()[:16]))
order = ["arm64-v8a", "armeabi-v7a", "x86_64", "x86"]
for i, abi in enumerate(order):
    want = blob[32 + i * 32: 64 + i * 32]
    with zipfile.ZipFile(apk) as z:
        try:
            lib = z.read("lib/%s/libnd.so" % abi)
        except KeyError:
            sys.exit("BUILD FAILED: lib/%s/libnd.so missing" % abi)
    got = hashlib.sha256(lib).digest()
    if want != got:
        sys.exit("BUILD FAILED: native self-hash mismatch for %s" % abi)
print("==> integrity: code digest == classes.dex == %s..." % got_dex.hex()[:16])
print("==> integrity: native self-hash  == 4 ABIs OK")
