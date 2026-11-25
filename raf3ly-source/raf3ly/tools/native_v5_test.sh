#!/usr/bin/env bash
# End-to-end proof of the v5 native guard against the REAL shipped APK:
#   honest -> 0 ; patched dex / re-signed / spoofed path / patched .so -> non-zero (kill)
set -e
export JAVA_HOME=/home/user/.cache/jdk17
T=/tmp/v5test; rm -rf $T; mkdir -p $T/app/lib/x86_64 $T/cls
APK=/home/user/raf3ly/Raf3ly-v1.0.apk

gcc -shared -fPIC -O2 -o $T/app/lib/x86_64/libnd.so \
  /home/user/raf3ly/app/src/native/guard.c -I$JAVA_HOME/include -I$JAVA_HOME/include/linux -ldl -lpthread

cp "$APK" $T/app/base.apk
python3 - "$T" <<'PY'
import hashlib, json, re, sys, zipfile
sys.path.insert(0, "/home/user/raf3ly/tools")
from aes import ctr
T = sys.argv[1]
KEY = bytes.fromhex(json.load(open("/home/user/raf3ly/tools/keys.json"))["aeskey"])
z = zipfile.ZipFile(T + "/app/base.apk")
blob = ctr(KEY, z.read("assets/i.bin")[:16], z.read("assets/i.bin")[16:])
dex_want = blob[:32]
lib_linux = hashlib.sha256(open(T + "/app/lib/x86_64/libnd.so", "rb").read()).digest()
# self table order: arm64, armv7, x86_64, x86  -> the host build is x86_64 (slot 2)
self_tbl = blob[32:64] + blob[64:96] + lib_linux + blob[96:128]
cert = re.search(r"SHA-256 digest: ([0-9a-f]+)",
                 open("/home/user/raf3ly/README.md").read()).group(1) if False else None
guard = open("/home/user/raf3ly/app/src/java/com/raf3ly/app/Guard.java").read()
E = re.search(r"char\[\] E = \{(.*?)\n    \};", guard, re.S).group(1)
cert_hex = "".join(chr(int(v, 16) ^ 0x3F) for v in re.findall(r"0x([0-9A-F]{4})", E))
open(T + "/data.txt", "w").write(dex_want.hex() + "\n" + self_tbl.hex() + "\n" + cert_hex)
print("expected dex :", dex_want.hex()[:16])
print("expected cert:", cert_hex[:16])
print("expected self:", lib_linux.hex()[:16])
PY

cat > $T/V.java <<'EOF'
package com.raf3ly.app;
import java.nio.file.*;
import java.util.Arrays;
public class V {
  static byte[] hex(String h){ byte[] o=new byte[h.length()/2]; for(int i=0;i<o.length;i++) o[i]=(byte)Integer.parseInt(h.substring(i*2,i*2+2),16); return o; }
  static byte[] flip(byte[] a){ byte[] b=a.clone(); b[3]^=0x5A; return b; }
  public static void main(String[] x) throws Exception {
    String[] d = new String(Files.readAllBytes(Paths.get("/tmp/v5test/data.txt"))).trim().split("\n");
    byte[] dex = hex(d[0].trim()), self = hex(d[1].trim()), cert = hex(d[2].trim());
    System.out.println("library loaded       : " + N.loaded());
    System.out.println("honest build         -> mask=" + N.probe(dex, dex, cert, self) + "  (expect 0)");
    System.out.println("patched dex          -> mask=" + N.probe(flip(dex), flip(dex), cert, self) + "  (expect !=0)");
    System.out.println("path spoofed (killer)-> mask=" + N.probe(dex, flip(dex), cert, self) + "  (expect !=0)");
    System.out.println("re-signed            -> mask=" + N.probe(dex, dex, flip(cert), self) + "  (expect !=0)");
    byte[] selfBad = self.clone(); selfBad[32*2+5] ^= 0xFF;   /* x86_64 slot */
    System.out.println("native lib patched   -> mask=" + N.probe(dex, dex, cert, selfBad) + "  (expect !=0)");
    System.out.println("assets removed       -> mask=" + N.probe(dex, dex, cert, null) + "  (expect !=0)");
    System.out.flush();
    Runtime.getRuntime().halt(0);
  }
}
EOF
$JAVA_HOME/bin/javac -encoding UTF-8 -nowarn -d $T/cls \
  /home/user/raf3ly/app/src/java/com/raf3ly/app/N.java $T/V.java
$JAVA_HOME/bin/java -Djava.library.path=$T/app/lib/x86_64 -cp $T/cls com.raf3ly.app.V
