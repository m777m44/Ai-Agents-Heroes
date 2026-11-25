#!/usr/bin/env python3
"""Simulates what a cracker does with NP Manager: patch one byte of code, re-pack, re-sign.
Proves the two independent checks both fire."""
import hashlib, json, os, re, shutil, subprocess, sys, zipfile
sys.path.insert(0, "/home/user/raf3ly/tools")
from aes import ctr

ROOT = "/home/user/raf3ly"
BT = "/home/user/.cache/android-sdk/build-tools/34.0.0"
KEY = bytes.fromhex(json.load(open(ROOT + "/tools/keys.json"))["aeskey"])
SRC = ROOT + "/Raf3ly-v1.0.apk"
OUT = "/tmp/tamper/Raf3ly-patched.apk"

os.makedirs("/tmp/tamper", exist_ok=True)

# 1) patch a byte inside classes.dex and rebuild the zip
with zipfile.ZipFile(SRC) as zin:
    names = zin.namelist()
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for n in names:
            data = zin.read(n)
            if n == "classes.dex":
                b = bytearray(data)
                b[len(b) // 2] ^= 0xFF          # one flipped instruction byte
                data = bytes(b)
            zout.writestr(n, data)

# 2) re-sign with a random key, exactly like a repack tool
ks = "/tmp/tamper/fake.keystore"
if not os.path.exists(ks):
    subprocess.run(["/home/user/.cache/jdk17/bin/keytool", "-genkeypair", "-keystore", ks, "-alias", "fake",
                    "-keyalg", "RSA", "-keysize", "2048", "-validity", "9999", "-storetype", "JKS", "-storepass", "fake123",
                    "-keypass", "fake123", "-dname", "CN=Fake"], check=True, capture_output=True)
signed = "/tmp/tamper/Raf3ly-patched-signed.apk"
subprocess.run([BT + "/apksigner", "sign", "--ks", ks, "--ks-pass", "pass:fake123",
                "--key-pass", "pass:fake123", "--ks-key-alias", "fake", "--min-sdk-version", "21",
                "--out", signed, OUT], check=True, capture_output=True)

# 3) check 1: signature
certs = subprocess.run([BT + "/apksigner", "verify", "--print-certs", signed],
                       capture_output=True, text=True).stdout
patched_cert = re.search(r"SHA-256 digest: ([0-9a-f]+)", certs).group(1)
guard = open(ROOT + "/app/src/java/com/raf3ly/app/Guard.java").read()
E = re.search(r"char\[\] E = \{(.*?)\n    \};", guard, re.S).group(1)
expect = "".join(chr(int(v, 16) ^ 0x3F) for v in re.findall(r"0x([0-9A-F]{4})", E))

# 4) check 2: code digest
with zipfile.ZipFile(SRC) as z:
    good = hashlib.sha256(z.read("classes.dex")).digest()
    blob = z.read("assets/i.bin")
recorded = ctr(KEY, blob[:16], blob[16:])
with zipfile.ZipFile(signed) as z:
    patched = hashlib.sha256(z.read("classes.dex")).digest()

print("signature check : shipped %s…  patched %s…  -> %s"
      % (expect[:12], patched_cert[:12], "CRASH (Guard.die)" if patched_cert != expect else "PASS"))
print("code check      : recorded %s…  patched %s…  -> %s"
      % (recorded.hex()[:12], patched.hex()[:12], "CRASH + poisoned strings" if patched != recorded else "PASS"))
print("untouched dex   : recorded %s…  original %s…  -> %s"
      % (recorded.hex()[:12], good.hex()[:12], "OK" if recorded == good else "BROKEN BUILD"))
