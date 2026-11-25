#!/usr/bin/env bash
# Compiles the guard source for the host JVM and proves the native decision logic:
# matching digests -> 0, patched code / new signature -> non-zero (=> crash).
set -e
export JAVA_HOME=/home/user/.cache/jdk17
T=/tmp/nativetest; rm -rf $T; mkdir -p $T/lib $T/cls
gcc -shared -fPIC -O2 -o $T/lib/libnd.so \
  /home/user/raf3ly/app/src/native/guard.c \
  -I$JAVA_HOME/include -I$JAVA_HOME/include/linux
cat > $T/JTest.java <<EOF
package com.raf3ly.app;
import java.util.Arrays;
public class JTest {
  static byte[] b(int v) { byte[] a = new byte[32]; Arrays.fill(a, (byte) v); return a; }
  public static void main(String[] x) throws Exception {
    byte[] d = b(7), c = b(9);
    System.out.println("library loaded   : " + N.loaded());
    System.out.println("all match        -> mask=" + N.verify(d, d, c, c) + "   (expect 0)");
    System.out.println("code patched     -> mask=" + N.verify(b(8), d, c, c) + "  (expect !=0 -> CRASH)");
    System.out.println("re-signed        -> mask=" + N.verify(d, d, b(10), c) + "  (expect !=0 -> CRASH)");
    System.out.println("both changed     -> mask=" + N.verify(b(1), d, b(2), c) + "  (expect !=0 -> CRASH)");
    System.out.println("digest removed   -> mask=" + N.verify(null, d, c, c) + "  (expect !=0 -> CRASH)");
  }
}
EOF
$JAVA_HOME/bin/javac -encoding UTF-8 -nowarn -d $T/cls \
  /home/user/raf3ly/app/src/java/com/raf3ly/app/N.java $T/JTest.java
$JAVA_HOME/bin/java -Djava.library.path=$T/lib -cp $T/cls com.raf3ly.app.JTest
