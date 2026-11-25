#!/usr/bin/env bash
# Raf3ly build
#   res → R.java → javac → R8 → classes.dex → (dex hash → encrypted assets) → link → zip → align → sign
set -e

export JAVA_HOME=/home/user/.cache/jdk17
export PATH=$JAVA_HOME/bin:$PATH
SDK=/home/user/.cache/android-sdk
BT=$SDK/build-tools/34.0.0
PLATFORM=$SDK/platforms/android-34/android.jar
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC=$ROOT/app/src
OUT=$ROOT/build
JAVAC=$JAVA_HOME/bin/javac
VER_CODE=1
VER_NAME="1"
APK=$ROOT/Raf3ly-v1.0.apk

rm -rf "$OUT"; mkdir -p "$OUT/classes" "$OUT/gen" "$OUT/flat" "$OUT/r8" "$OUT/assets"

# ---- signing identity: keep Guard.java in sync with the key that signs this build ----
if [ -f "$ROOT/signing.conf" ]; then
  . "$ROOT/signing.conf"
else
  KEYSTORE=$ROOT/release.keystore; ALIAS=raf3ly; STOREPASS=$(grep STOREPASS "$ROOT/keystore-info.txt" | cut -d= -f2)
fi
CERT_SHA=$(bash "$ROOT/tools/cert-sha256.sh" "$KEYSTORE" "$ALIAS" "$STOREPASS")
echo "==> signer cert SHA-256: $CERT_SHA"

echo "==> aapt2 compile"
"$BT/aapt2" compile --dir "$SRC/res" -o "$OUT/flat/res.zip"

echo "==> aapt2 link (R.java)"
"$BT/aapt2" link -o "$OUT/base0.apk" \
  -I "$PLATFORM" --manifest "$SRC/AndroidManifest.xml" -R "$OUT/flat/res.zip" \
  --java "$OUT/gen" --min-sdk-version 21 --target-sdk-version 34 \
  --version-code $VER_CODE --version-name "$VER_NAME" --no-version-vectors --auto-add-overlay

echo "==> build stamp"
python3 "$ROOT/tools/gen_stamp.py"

echo "==> encrypting any new plain-text literals"
python3 "$ROOT/tools/enc_strings_all.py" | tail -2

echo "==> javac"
"$JAVAC" -encoding UTF-8 -nowarn -source 8 -target 8 \
  -classpath "$PLATFORM" -d "$OUT/classes" \
  $(find "$SRC/java" "$OUT/gen" -name '*.java')

echo "==> R8 (obfuscation)"
"$JAVA_HOME/bin/java" -cp "$BT/lib/d8.jar" com.android.tools.r8.R8 \
  --release --min-api 21 --lib "$PLATFORM" \
  --pg-conf "$ROOT/proguard.txt" --output "$OUT/r8" \
  $(find "$OUT/classes" -name '*.class')

echo "==> packing assets + code digest"
python3 "$ROOT/tools/pack_assets.py"

echo "==> aapt2 link (final, with assets)"
"$BT/aapt2" link -o "$OUT/base.apk" \
  -I "$PLATFORM" --manifest "$SRC/AndroidManifest.xml" -R "$OUT/flat/res.zip" \
  -A "$OUT/assets" \
  --min-sdk-version 21 --target-sdk-version 34 \
  --version-code $VER_CODE --version-name "$VER_NAME" --no-version-vectors --auto-add-overlay

echo "==> package"
cp "$OUT/base.apk" "$OUT/unaligned.apk"
# classes.dex is STORED (not deflated) so the native guard can hash it without inflate
(cd "$OUT/r8" && zip -0 -q -j "$OUT/unaligned.apk" classes.dex)

"$BT/zipalign" -f -p 4 "$OUT/unaligned.apk" "$OUT/aligned.apk"

echo "==> sign (release key)"
KS=$KEYSTORE
PASS=$STOREPASS
"$BT/apksigner" sign --ks "$KS" --ks-pass "pass:$PASS" --key-pass "pass:$PASS" \
  --ks-key-alias "$ALIAS" --min-sdk-version 21 \
  --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true \
  --out "$APK" "$OUT/aligned.apk"

"$BT/apksigner" verify --print-certs "$APK" | head -4

# ---- release signature printout ----
APK_SHA=$("$BT/apksigner" verify --print-certs "$APK" | grep "SHA-256 digest" | head -1 | sed 's/.*: //' | tr -d ' ')
echo "==> signed with: $APK_SHA"
echo "==> done"
ls -lh "$APK"
