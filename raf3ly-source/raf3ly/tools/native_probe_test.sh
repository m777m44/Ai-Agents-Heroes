#!/usr/bin/env bash
# End-to-end test of the native probe on the host: builds a fake install layout
# (appdir/lib/<abi>/libnd.so + appdir/base.apk) and checks every mask bit.
set -e
export JAVA_HOME=/home/user/.cache/jdk17
T=/tmp/probe; rm -rf $T; mkdir -p $T/app/lib/x86_64 $T/cls
gcc -shared -fPIC -O2 -o $T/app/lib/x86_64/libnd.so \
  /home/user/raf3ly/app/src/native/guard.c -I$JAVA_HOME/include -I$JAVA_HOME/include/linux -ldl
python3 - "$T" <<'PY'
import hashlib, sys, zipfile, os
t = sys.argv[1]
dex = b"dex\n035\x00" + bytes(range(256)) * 40
open(t + "/dex.bin", "wb").write(dex)
# real package: classes.dex STORED
with zipfile.ZipFile(t + "/app/base.apk", "w", zipfile.ZIP_STORED) as z:
    z.writestr("AndroidManifest.xml", b"<manifest/>")
    z.writestr("classes.dex", dex)
open(t + "/want.hex", "w").write(hashlib.sha256(dex).hexdigest())
# repacked package: classes.dex DEFLATE (what a repacker usually produces)
with zipfile.ZipFile(t + "/app/base-deflate.apk", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("classes.dex", dex)
PY
cat > $T/P.java <<'EOF'
package com.raf3ly.app;
import java.nio.file.*;
public class P {
  static byte[] hex(String h) {
    byte[] o = new byte[32];
    for (int i = 0; i < 32; i++) o[i] = (byte) Integer.parseInt(h.substring(i*2, i*2+2), 16);
    return o;
  }
  static byte[] flip(byte[] a) { byte[] b = a.clone(); b[0] ^= 0xFF; return b; }
  public static void main(String[] x) throws Exception {
    byte[] want = hex(new String(Files.readAllBytes(Paths.get("/tmp/probe/want.hex"))).trim());
    byte[] cert = new byte[32]; java.util.Arrays.fill(cert, (byte) 3);
    System.out.println("library loaded        : " + N.loaded());
    System.out.println("honest build          -> mask=" + N.probe(want, want, cert, cert) + "  (expect 0)");
    System.out.println("code patched          -> mask=" + N.probe(flip(want), flip(want), cert, cert) + "  (expect !=0)");
    System.out.println("path spoofed (APKKiller) -> mask=" + N.probe(flip(want), want, cert, cert) + "  (expect !=0)");
    System.out.println("re-signed             -> mask=" + N.probe(want, want, cert, flip(cert)) + "  (expect !=0)");
  }
}
EOF
$JAVA_HOME/bin/javac -encoding UTF-8 -nowarn -d $T/cls \
  /home/user/raf3ly/app/src/java/com/raf3ly/app/N.java $T/P.java
$JAVA_HOME/bin/java -Djava.library.path=$T/app/lib/x86_64 -cp $T/cls com.raf3ly.app.P
echo "--- same package but classes.dex recompressed (repacker default) ---"
cp $T/app/base.apk $T/app/base.bak && cp $T/app/base-deflate.apk $T/app/base.apk
$JAVA_HOME/bin/java -Djava.library.path=$T/app/lib/x86_64 -cp $T/cls com.raf3ly.app.P | head -3
mv $T/app/base.bak $T/app/base.apk
