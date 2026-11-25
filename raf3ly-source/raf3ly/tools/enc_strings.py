#!/usr/bin/env python3
"""Replaces sensitive literals in Java sources with S.d("<base64+xor>") calls."""
import base64, json, re, sys
ROOT = "/home/user/raf3ly/app/src/java/com/raf3ly/app/"
K1 = bytes.fromhex(json.load(open("/home/user/raf3ly/tools/keys.json"))["k1"])

def enc(s):
    b = s.encode("utf-8")
    return base64.b64encode(bytes(v ^ K1[i % len(K1)] for i, v in enumerate(b))).decode()

def sub_literal(text, value):
    return 'S.d("%s")' % enc(value)

def patch(path, fn):
    p = ROOT + path
    s = open(p, encoding="utf-8").read()
    n = fn(s)
    if n != s:
        open(p, "w", encoding="utf-8").write(n)
        print("patched", path)

# 1) every https URL literal -> S.d(...)
def urls(s):
    def rep(m):
        val = m.group(1)
        if val.startswith("S.d("):
            return m.group(0)
        return sub_literal(None, val)
    s = re.sub(r'"(https://[^"\\]*)"', rep, s)
    # the tmpfiles regex (contains escaped quotes) handled explicitly
    s = s.replace('Pattern.compile("https://tmpfiles[.]org/dl/[^\\"\'<> ]+")',
                  'Pattern.compile(S.d("%s"))' % enc('https://tmpfiles[.]org/dl/[^"\'<> ]+'))
    return s

# 2) Host catalog: name + domain columns
def hostnames(s):
    def rep(m):
        return 'new Host("%s", %s, %s,' % (m.group(1), sub_literal(None, m.group(2)), sub_literal(None, m.group(3)))
    return re.sub(r'new Host\("([a-z0-9]+)", "([^"]+)", "([^"]+)",', rep, s)

patch("Hosts.java", lambda s: hostnames(urls(s)))
patch("Brand.java", urls)
print("done")
